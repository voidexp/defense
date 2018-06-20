#include "init.h"
#include "renderer.h"
#include <SDL.h>
#include <stdbool.h>

SDL_Window *g_window = NULL;
SDL_Renderer *g_renderer = NULL;

extern beer_err
beer_py_init(void);

extern void
beer_py_fini(void);

static bool initialized = false;

beer_err
beer_init(unsigned win_w, unsigned win_h)
{
	if (SDL_Init(SDL_INIT_VIDEO) < 0)
	{
		return BEER_ERR_INIT;
	}

	g_window = SDL_CreateWindow(
		"Beer",
		SDL_WINDOWPOS_CENTERED,
		SDL_WINDOWPOS_CENTERED,
		(int)win_w,
		(int)win_h,
		0
	);
	if (!g_window)
	{
		return BEER_ERR_INIT;
	}

	g_renderer = SDL_CreateRenderer(
		g_window,
		-1,
		SDL_RENDERER_ACCELERATED
	);
	if (!g_renderer)
	{
		return BEER_ERR_INIT;
	}

	SDL_SetRenderDrawBlendMode(g_renderer, SDL_BLENDMODE_BLEND);

	beer_err err = beer_py_init();
	if (err != BEER_OK)
	{
		return err;
	}

	static bool finalizer_registered = false;
	if (!finalizer_registered)
	{
		atexit(beer_fini);
		finalizer_registered = true;
	}

	initialized = true;

#ifdef DEBUG
	printf("Core initialized\n");
#endif

	return BEER_OK;
}

beer_err
beer_start(void)
{
	SDL_Event evt;
	beer_err err = BEER_OK;
	bool run = true;

	while (run && !err)
	{
		while (SDL_PollEvent(&evt))
		{
			switch (evt.type)
			{
			case SDL_QUIT:
				run = false;
				break;
			}
		}

		if ((err = beer_renderer_clear()) ||
		    (err = beer_renderer_present()))
		{
			break;
		}
	}

	return err;
}

void
beer_fini(void)
{
	if (!initialized)
	{
		return;
	}

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

	initialized = false;

#ifdef DEBUG
	printf("Core finalized\n");
#endif
}
