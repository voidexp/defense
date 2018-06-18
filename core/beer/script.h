#pragma once

#include "error.h"

struct BeerScript
{
	// script path
	char *path;

	// private
	void *data_;
};

beer_err
beer_script_load(const char *path, struct BeerScript **r_script);

void
beer_script_free(struct BeerScript *script);

beer_err
beer_script_init(struct BeerScript *script);

beer_err
beer_script_fini(struct BeerScript *script);
