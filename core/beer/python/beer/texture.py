from _beer import lib, ffi  # pylint: disable=import-error,no-name-in-module


class Texture:

    def __init__(self):
        self.__tex = ffi.new('struct BeerTexture*')
        lib.beer_texture_from_data(self.__tex, lib.BEER_TEXTURE_RGBA8888, ffi.NULL, 0)
        print('texture created')

    def __del__(self):
        lib.beer_texture_free(self.__tex)
        print('texture destroyed')
