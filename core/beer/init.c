#include "init.h"
#include <SDL.h>

SDL_Window *g_window = NULL;
SDL_Renderer *g_renderer = NULL;

extern beer_err
beer_py_init(void);

extern void
beer_py_fini(void);

beer_err
beer_init(unsigned win_w, unsigned win_h)
{
	if (SDL_Init(SDL_INIT_VIDEO) < 0)
	{
		return BEER_ERR_INIT;
	}

	int rc = SDL_CreateWindowAndRenderer(
		win_w,
		win_h,
		0,
		&g_window,
		&g_renderer
	);
	if (rc != 0 || g_window == NULL || g_renderer == NULL)
	{
		return BEER_ERR_INIT;
	}

	beer_err err = beer_py_init();
	if (err != BEER_OK)
	{
		return err;
	}

	atexit(beer_fini);

	return BEER_OK;
}

void
beer_fini(void)
{
	beer_py_fini();

	if (SDL_WasInit(SDL_INIT_VIDEO))
	{
		if (g_window)
		{
			SDL_DestroyWindow(g_window);
			g_window = NULL;
		}

		if (g_renderer)
		{
			SDL_DestroyRenderer(g_renderer);
			g_renderer = NULL;
		}

		SDL_Quit();
	}
}
