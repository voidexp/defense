#define _DEFAULT_SOURCE

#include "error.h"
#include "fs.h"
#include <assert.h>
#include <errno.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>

#ifdef BEER_ON_UNIX
# include <unistd.h>
# include <dirent.h>
#endif

extern int errno;

static beer_err
errno_to_beer_err(void)
{
	switch (errno)
	{
	case EACCES:
		return BEER_ERR_FS_NO_ACCESS;
	case ENOENT:
		return BEER_ERR_FS_NO_ENTRY;
	case ENOTDIR:
		return BEER_ERR_FS_NOT_A_DIR;
	case EISDIR:
		return BEER_ERR_FS_NOT_A_FILE;
	default:
		return BEER_ERR_FS_GENERIC;
	}
}

beer_err
beer_dir_list(const char *path, char **r_paths[], int *r_paths_len)
{
#ifdef BEER_ON_UNIX
	// open the directory
	DIR *dir = opendir(path);
	if (dir == NULL)
	{
		return errno_to_beer_err();
	}

	// read the number of entries and reset the reading to the beginning
	size_t len = 0;
	struct dirent *dirent;
	long pos = telldir(dir);
	while ((dirent = readdir(dir)))
	{
		len++;
	}
	seekdir(dir, pos);

	// allocate an array of string pointers and fill it with entry names
	char **paths = malloc(len * sizeof(char*));
	int i = 0;
	while ((dirent = readdir(dir)))
	{
		paths[i++] = strndup(dirent->d_name, 256);
	}

	closedir(dir);

	*r_paths = paths;
	*r_paths_len = len;
#endif

	return BEER_OK;
}

beer_err
beer_file_get_type(const char *path, enum BeerFileType *type)
{
	assert(path);
	assert(type);

#ifdef BEER_ON_UNIX
	struct stat st;
	if (stat(path, &st) != 0)
	{
		return errno_to_beer_err();
	}

	if (S_ISDIR(st.st_mode))
	{
		*type = BEER_FILE_TYPE_DIRECTORY;
	}
	else if (S_ISREG(st.st_mode))
	{
		*type = BEER_FILE_TYPE_FILE;
	}
	else
	{
		*type = BEER_FILE_TYPE_OTHER;
	}
#endif

	return BEER_OK;
}

beer_err
beer_file_read(const char *path, char **r_data, size_t *r_size)
{
	assert(path);
	assert(r_data);

	struct stat st;
	size_t size = 0;
	beer_err err = BEER_OK;
	FILE *fp = NULL;
	*r_data = NULL;

	if (stat(path, &st) != 0)
	{
		return errno_to_beer_err();
	}

	size = st.st_size;

	if (size > 0)
	{
		fp = fopen(path, "rb");
		if (fp == NULL)
		{
			err = errno_to_beer_err();
			goto cleanup;
		}

		*r_data = malloc(size + 1);
		if (!*r_data)
		{
			err = BEER_ERR_NO_MEM;
			goto cleanup;
		}
		(*r_data)[size] = 0;  // NUL-terminator

		size_t actual_size = fread(*r_data, 1, size, fp);
		if (actual_size != size)
		{
			err = BEER_ERR_IO;
			goto cleanup;
		}
	}

cleanup:
	if (fp)
	{
		if (fclose(fp) != 0 && !err)
		{
			err = errno_to_beer_err();
		}
	}

	if (err)
	{
		free(*r_data);
		*r_data = NULL;
		size = 0;
	}

	if (r_size)
	{
		*r_size = size;
	}

	return err;
}

char*
beer_path_join(const char **paths, int paths_len)
{
	assert(paths);
	assert(paths_len > 0);

	size_t len = 0;
	char *path = NULL;
	for (int i = 0; i < paths_len; i++)
	{
		const char *s = paths[i];
		assert(s);

		len += strlen(s) + 1;
		char *newpath = malloc(len);

		if (path)
		{
			snprintf(newpath, len, "%s/%s", path, s);
		}
		else
		{
			snprintf(newpath, len, "%s", s);
		}

		free(path);
		path = newpath;
	}

	return path;
}

bool
beer_path_exists(const char *path)
{
	assert(path);

	struct stat st;
	int exists = stat(path, &st) == 0;
	errno = 0;
	return exists;
}
