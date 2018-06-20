#include "texture.h"
#include "memory.h"
#include <SDL.h>
#include <assert.h>

extern SDL_Renderer *g_renderer;

static inline int
beer_pixel_format_to_sdl(enum BeerPixelFormat fmt)
{
	switch (fmt)
	{
	case BEER_PIXEL_FORMAT_RGBA8888:
		return SDL_PIXELFORMAT_RGBA32;
	default:
		return SDL_PIXELFORMAT_UNKNOWN;
	}
}

static inline int
beer_pixel_format_bpp(enum BeerPixelFormat fmt)
{
	switch (fmt)
	{
	case BEER_PIXEL_FORMAT_RGBA8888:
		return 4;
	default:
		return 0;
	}
}

beer_err
beer_texture_from_buffer(enum BeerPixelFormat fmt, int width, int height, char *data, struct BeerTexture **r_tex)
{
	assert(fmt > BEER_PIXEL_FORMAT_UNKNOWN && fmt < BEER_PIXEL_FORMAT_MAX);
	assert(width > 0);
	assert(height > 0);
	assert(data);
	assert(r_tex);

	// create a SDL_Texture instance
	SDL_Texture *sdl_tex = SDL_CreateTexture(
		g_renderer,
		beer_pixel_format_to_sdl(fmt),
		SDL_TEXTUREACCESS_STATIC,
		width,
		height
	);
	if (!sdl_tex)
	{
		return BEER_ERR_SDL;
	}

	// enable alpha-blending for the texture (VERY IMPORTANT)
	SDL_SetTextureBlendMode(sdl_tex, SDL_BLENDMODE_BLEND);

	// copy the texture data
	int pitch = width * beer_pixel_format_bpp(fmt);
	if (SDL_UpdateTexture(sdl_tex, NULL, data, pitch) != 0)
	{
		SDL_DestroyTexture(sdl_tex);
		return BEER_ERR_SDL;
	}

	// create and fill a BeerTexture
	struct BeerTexture *tex = NULL;
	beer_err err = beer_new(struct BeerTexture, &tex);
	if (err)
	{
		return err;
	}

	tex->width = width;
	tex->height = height;
	tex->format = fmt;
	tex->data_ = (void*)sdl_tex;

	*r_tex = tex;

	return BEER_OK;
}

void
beer_texture_free(struct BeerTexture *tex)
{
	if (tex)
	{
		SDL_DestroyTexture((SDL_Texture*)tex->data_);
		beer_free(tex);
	}
}
