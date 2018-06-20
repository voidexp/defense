from _beer import lib, ffi  # pylint: disable=import-error,no-name-in-module
from PIL import Image
from enum import IntEnum
from enum import unique


@unique
class PixelFormat(IntEnum):

    RGBA8888 = lib.BEER_PIXEL_FORMAT_RGBA8888


class Texture:

    def __init__(self, filename):
        self.__tex = ffi.new('struct BeerTexture**', ffi.NULL)

        img = Image.open(filename).convert('RGBA')

        err = lib.beer_texture_from_buffer(
            PixelFormat.RGBA8888,
            img.width,
            img.height,
            ffi.from_buffer(img.tobytes()),
            self.__tex
        )
        if err:
            raise RuntimeError('failed to create texture from "{}"'.format(filename))

    def __del__(self):
        lib.beer_texture_free(self.pointer)

    @property
    def width(self):
        return self.pointer.width

    @property
    def height(self):
        return self.pointer.height

    @property
    def format(self):
        return {item.value: item.name for item in PixelFormat}[self.pointer.format]

    @property
    def pointer(self):
        return self.__tex[0]
