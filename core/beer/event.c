#include "event.h"
#include <assert.h>
#include <SDL.h>

static struct BeerKeyState keys[BEER_KEY_MAX] = {{.pressed = 0}};

static enum BeerKeyCode
sdlk_to_beer(SDL_Keycode code)
{
	switch (code)
	{
	case SDLK_w: return BEER_KEY_W;
	case SDLK_a: return BEER_KEY_A;
	case SDLK_s: return BEER_KEY_S;
	case SDLK_d: return BEER_KEY_D;
	case SDLK_ESCAPE: return BEER_KEY_ESC;
	case SDLK_SPACE: return BEER_KEY_SPACE;
	default: return BEER_KEY_UNKNOWN;
	}
}

static void
handle_key_event(const SDL_KeyboardEvent *evt)
{
	struct BeerKeyState *state = &keys[sdlk_to_beer(evt->keysym.sym)];
	state->pressed = evt->type == SDL_KEYDOWN;
}

void
handle_sdl_event(const SDL_Event *evt)
{
	switch (evt->type)
	{
	case SDL_KEYDOWN:
	case SDL_KEYUP:
		handle_key_event(&evt->key);
		break;
	}
}

BEER_API beer_err
beer_key_get_state(enum BeerKeyCode key, struct BeerKeyState *r_state)
{
	assert(r_state);
	assert(key >= 0 && key < BEER_KEY_MAX);

	*r_state = keys[key];

	return BEER_OK;
}
