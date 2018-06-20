#include "memory.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

beer_err
beer_alloc(size_t size, void **r_ptr)
{
	assert(r_ptr);
	*r_ptr = malloc(size);
	if (!*r_ptr)
	{
		return BEER_ERR_NO_MEM;
	}
	return BEER_OK;
}

beer_err
beer_alloc0(size_t size, void **r_ptr)
{
	assert(r_ptr);
	beer_err err = beer_alloc(size, r_ptr);
	if (!err)
	{
		memset(*r_ptr, 0, size);
	}
	return err;
}

void
beer_free(void *ptr)
{
	free(ptr);
}
