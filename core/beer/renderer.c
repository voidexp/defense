#include "renderer.h"
#include "primitives.h"
#include "texture.h"
#include "sprite.h"
#include <assert.h>
#include <SDL.h>

#define RENDER_LIST_LEN 2048

extern SDL_Renderer *g_renderer;

enum NodeType
{
	NODE_TYPE_NONE,
	NODE_TYPE_SPRITE,
};

struct BeerRenderNode
{
	enum NodeType type;
	void *data;
};

static struct BeerRenderNode render_list[RENDER_LIST_LEN] = {{NODE_TYPE_NONE, NULL}};

static beer_err
alloc_node(struct BeerRenderNode **r_node)
{
	for (unsigned long i = 0; i < RENDER_LIST_LEN; i++)
	{
		if (render_list[i].type == NODE_TYPE_NONE)
		{
			*r_node = render_list + i;
			return BEER_OK;
		}
	}
	return BEER_ERR_RENDER_QUEUE_FULL;
}

static beer_err
remove_node(struct BeerRenderNode *node)
{
	for (unsigned long i = 0; i < RENDER_LIST_LEN; i++)
	{
		if (node == render_list + i)
		{
			memset(node, 0, sizeof(struct BeerRenderNode));
			return BEER_OK;
		}
	}
	return BEER_ERR_RENDER_BAD_NODE;
}

static beer_err
render_sprite(struct BeerSprite *sprite)
{
	struct BeerRect rect = sprite->sheet->frames[sprite->frame];
	struct BeerTexture *tex = sprite->sheet->texture;

	SDL_Rect src = {
		.x = rect.x,
		.y = rect.y,
		.w = (int)rect.width,
		.h = (int)rect.height,
	};
	SDL_Rect dst = src;
	dst.x = roundf(sprite->x);
	dst.y = roundf(sprite->y);

	int result = SDL_RenderCopy(
		g_renderer,
		(SDL_Texture*)tex->data_,
		&src,
		&dst
	);
	if (result != 0)
	{
		return BEER_ERR_SDL;
	}
	return BEER_OK;
}

beer_err
beer_renderer_add_sprite_node(struct BeerSprite *sprite, struct BeerRenderNode **r_node)
{
	assert(sprite);
	assert(r_node);
	beer_err err = alloc_node(r_node);
	if (err)
	{
		return err;
	}

	(*r_node)->type = NODE_TYPE_SPRITE;
	(*r_node)->data = (void*)sprite;

	return BEER_OK;
}

beer_err
beer_renderer_remove_node(struct BeerRenderNode *node)
{
	return remove_node(node);
}

beer_err
beer_renderer_clear(void)
{
	if (SDL_RenderClear(g_renderer) != 0)
	{
		return BEER_ERR_SDL;
	}
	return BEER_OK;
}

beer_err
beer_renderer_present(void)
{
	beer_err err = BEER_OK;

	for (unsigned int i = 0; i < RENDER_LIST_LEN; i++)
	{
		struct BeerRenderNode node = render_list[i];
		if (node.type == NODE_TYPE_SPRITE)
		{
			err = render_sprite((struct BeerSprite*)node.data);
		}

		if (err)
		{
			break;
		}
	}

	SDL_RenderPresent(g_renderer);

	return err;
}
