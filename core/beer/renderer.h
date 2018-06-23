#pragma once

#include "defs.h"
#include "error.h"

struct BeerSprite;
struct BeerRenderNode;

BEER_API beer_err
beer_renderer_add_sprite_node(struct BeerSprite *sprite, struct BeerRenderNode **r_node);

BEER_API beer_err
beer_renderer_remove_node(struct BeerRenderNode *node);

BEER_API beer_err
beer_renderer_clear(void);

BEER_API beer_err
beer_renderer_present(void);
