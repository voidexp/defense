#pragma once

#include "defs.h"
#include "error.h"
#include <stdbool.h>

enum BeerKeyCode
{
	BEER_KEY_UNKNOWN,
	BEER_KEY_W,
	BEER_KEY_A,
	BEER_KEY_S,
	BEER_KEY_D,
	BEER_KEY_ESC,
	BEER_KEY_SPACE,
	BEER_KEY_MAX
};

struct BeerKeyState
{
	bool pressed;
};

BEER_API beer_err
beer_key_get_state(enum BeerKeyCode key, struct BeerKeyState *r_state);
