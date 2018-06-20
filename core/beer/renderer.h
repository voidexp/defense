#pragma once

#include "error.h"

struct BeerSprite;
struct BeerRenderNode;

beer_err
beer_renderer_add_sprite_node(struct BeerSprite *sprite, struct BeerRenderNode **r_node);

beer_err
beer_renderer_remove_node(struct BeerRenderNode *node);

beer_err
beer_renderer_clear(void);

beer_err
beer_renderer_present(void);
