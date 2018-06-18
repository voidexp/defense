from cffi import FFI


ffibuilder = FFI()


ffibuilder.set_source('_beer', """
#include "beer.h"
#include "error.h"
#include "texture.h"
""")


ffibuilder.cdef("""
typedef int beer_err;

struct BeerTexture
{
    // texture size in pixels
    unsigned width, height;

    // private
    void *data_;
};

enum BeerTextureFormat
{
    BEER_TEXTURE_RGBA8888
};

beer_err
beer_texture_from_data(struct BeerTexture *tex, enum BeerTextureFormat fmt, void *data, int pitch);

void
beer_texture_free(struct BeerTexture *tex);
""")


if __name__ == '__main__':
    ffibuilder.emit_c_code('beer_cffi.c')
