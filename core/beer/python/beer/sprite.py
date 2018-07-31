"""
2D sprite creation and rendering module.
"""
from typing import Sequence, Tuple, Any, cast, Optional
from _beer import lib, ffi
from beer.texture import Texture


class Sheet:
    """
    Spritesheet geometry on top of a texture.
    """

    def __init__(self, texture: Texture, frames: Sequence[Tuple[int, int, int, int]]) -> None:
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
    def pointer(self) -> Any:
        return self.__ptr


class Sprite:
    """
    2D sprite.
    """

    def __init__(self, sheet: Sheet) -> None:
        self.__ptr = ffi.new('struct BeerSprite*')
        self.__ptr.x = 0.0
        self.__ptr.y = 0.0
        self.__ptr.frame = 0
        self.__ptr.sheet = sheet.pointer
        self.__node = None
        self.__sheet = cast(Optional[Sheet], sheet)

    def __del__(self) -> None:
        self.visible = False
        self.__ptr.sheet = ffi.NULL
        self.__sheet = None

    @property
    def x(self) -> float:
        return cast(float, self.__ptr.x)

    @x.setter
    def x(self, value: float) -> None:
        self.__ptr.x = value

    @property
    def y(self) -> float:
        return cast(float, self.__ptr.y)

    @y.setter
    def y(self, value: float) -> None:
        self.__ptr.y = value

    @property
    def frame(self) -> int:
        return cast(int, self.__ptr.frame)

    @frame.setter
    def frame(self, index: int) -> None:
        self.__ptr.frame = index

    @property
    def visible(self) -> bool:
        return self.__node is not None

    @visible.setter
    def visible(self, flag: bool) -> None:
        if flag and self.__node is None:
            node = ffi.new('struct BeerRenderNode**', ffi.NULL)
            if lib.beer_renderer_add_sprite_node(self.__ptr, node) != 0:
                raise RuntimeError('failed to add sprite render node')
            self.__node = node
        elif not flag and self.__node is not None:
            if lib.beer_renderer_remove_node(self.__node[0]) != 0:
                raise RuntimeError('failed to remove sprite render node')
            self.__node = None
