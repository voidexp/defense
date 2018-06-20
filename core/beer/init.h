#pragma once

#include "error.h"

beer_err
beer_init(unsigned win_w, unsigned win_h);

beer_err
beer_start(void);

void
beer_fini(void);
