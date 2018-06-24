from _beer import lib, ffi  # pylint: disable=import-error,no-name-in-module


class Sheet:

    def __init__(self, texture, frames):
        self.__frames = ffi.new('struct BeerRect[{}]'.format(len(frames)))
        for i, frame in enumerate(frames):
            rect = self.__frames[i]
            rect.x, rect.y, rect.width, rect.height = frame

        self.__ptr = ffi.new('struct BeerSpriteSheet*')
        self.__ptr.texture = texture.pointer
        self.__ptr.frames = self.__frames
        self.__ptr.frames_len = len(frames)
        self.__texture = texture  # keep alive

    @property
    def pointer(self):
        return self.__ptr


class Sprite:

    def __init__(self, sheet):
        self.__ptr = ffi.new('struct BeerSprite*')
        self.__ptr.x = 0.0
        self.__ptr.y = 0.0
        self.__ptr.frame = 0
        self.__ptr.sheet = sheet.pointer
        self.__sheet = sheet  # keep alive
        self.__node = None

    def __del__(self):
        self.visible = False
        self.__ptr.sheet = ffi.NULL
        self.__sheet = None

    @property
    def x(self):
        return self.__ptr.x

    @x.setter
    def x(self, value):
        self.__ptr.x = value

    @property
    def y(self):
        return self.__ptr.y

    @y.setter
    def y(self, value):
        self.__ptr.y = value

    @property
    def visible(self):
        return self.__node is not None

    @visible.setter
    def visible(self, flag):
        if flag and self.__node is None:
            node = ffi.new('struct BeerRenderNode**', ffi.NULL)
            if lib.beer_renderer_add_sprite_node(self.__ptr, node) != 0:
                raise RuntimeError('failed to add sprite render node')
            self.__node = node
        elif not flag and self.__node is not None:
            if lib.beer_renderer_remove_node(self.__node[0]) != 0:
                raise RuntimeError('failed to remove sprite render node')
            self.__node = None
