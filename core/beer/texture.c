#include "texture.h"

#include <stdio.h>

beer_err
beer_texture_from_data(struct BeerTexture *tex, enum BeerTextureFormat fmt, void *data, int pitch)
{
	(void)tex;
	(void)fmt;
	(void)data;
	(void)pitch;

	printf("beer_texture_from_data(...)\n");

	return BEER_OK;
}

void
beer_texture_free(struct BeerTexture *tex)
{
	(void)tex;

	printf("beer_texture_free(...)\n");
}
