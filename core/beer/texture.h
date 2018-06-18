#pragma once

#include "error.h"

struct BeerTexture
{
	// texture size in pixels
	unsigned width, height;

	// private
	void *data_;
};

enum BeerTextureFormat
{
	BEER_TEXTURE_RGBA8888,
};

beer_err
beer_texture_from_data(struct BeerTexture *tex, enum BeerTextureFormat fmt, void *data, int pitch);

void
beer_texture_free(struct BeerTexture *tex);
