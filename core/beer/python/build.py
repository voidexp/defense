from cffi import FFI


ffibuilder = FFI()


ffibuilder.set_source('_beer', """
#include "beer.h"
""")


ffibuilder.cdef("""
typedef int beer_err;

struct BeerRect
{
    int x;
    int y;
    unsigned width;
    unsigned height;
};

enum BeerPixelFormat
{
    BEER_PIXEL_FORMAT_RGBA8888
};

struct BeerTexture
{
    // texture size in pixels
    unsigned width, height;

    enum BeerPixelFormat format;

    // private
    void *data_;
};

struct BeerSpriteSheet
{
    // sheet texture
    struct BeerTexture *texture;

    // frameset
    struct BeerRect *frames;
    unsigned int frames_len;
};

struct BeerSprite
{
    // position
    int x, y;

    // current frame
    int frame;

    // sheet
    struct BeerSpriteSheet *sheet;
};

struct BeerRenderNode;

beer_err
beer_texture_from_buffer(enum BeerPixelFormat fmt, int width, int height, char *data, struct BeerTexture **r_tex);

void
beer_texture_free(struct BeerTexture *tex);

beer_err
beer_renderer_add_sprite_node(struct BeerSprite *sprite, struct BeerRenderNode **r_node);

beer_err
beer_renderer_remove_node(struct BeerRenderNode *node);
""")


if __name__ == '__main__':
    ffibuilder.emit_c_code('_beer.c')
