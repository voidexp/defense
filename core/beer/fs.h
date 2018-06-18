#pragma once

#include "error.h"
#include <stdbool.h>
#include <stddef.h>

enum BeerFileType
{
	BEER_FILE_TYPE_OTHER,
	BEER_FILE_TYPE_DIRECTORY,
	BEER_FILE_TYPE_FILE
};

beer_err
beer_dir_list(const char *path, char **r_paths[], int *r_paths_len);

beer_err
beer_file_get_type(const char *path, enum BeerFileType *type);

beer_err
beer_file_read(const char *path, char **r_data, size_t *r_size);

bool
beer_path_exists(const char *path);

char*
beer_path_join(const char **paths, int paths_len);
