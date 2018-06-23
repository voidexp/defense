#pragma once

#include "defs.h"
#include "error.h"

struct BeerScript
{
	// script path
	char *path;

	// private
	void *data_;
};

BEER_API beer_err
beer_script_load(const char *path, struct BeerScript **r_script);

BEER_API void
beer_script_free(struct BeerScript *script);

BEER_API beer_err
beer_script_invoke_init(struct BeerScript *script);

BEER_API beer_err
beer_script_invoke_fini(struct BeerScript *script);
