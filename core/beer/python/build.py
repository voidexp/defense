from cffi import FFI


ffibuilder = FFI()


ffibuilder.set_source('_beer', """
#include "beer.h"
""")


ffibuilder.cdef("""
typedef int beer_err;

enum {
    BEER_OK
};

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
    float x, y;

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

beer_err
beer_key_get_state(enum BeerKeyCode key, struct BeerKeyState *r_state);
""")


if __name__ == '__main__':
    ffibuilder.emit_c_code('_beer.c')
