#pragma once

#include "defs.h"
#include "error.h"

BEER_API beer_err
beer_init(unsigned win_w, unsigned win_h);

BEER_API beer_err
beer_start(void);

BEER_API void
beer_fini(void);
