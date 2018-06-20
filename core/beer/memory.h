#pragma once

#include "error.h"
#include <stddef.h>

beer_err
beer_alloc(size_t size, void **r_ptr);

beer_err
beer_alloc0(size_t size, void **r_ptr);

#define beer_new(type, r_ptrptr) (beer_alloc0(sizeof(type), (void**)r_ptrptr))

void
beer_free(void *ptr);
