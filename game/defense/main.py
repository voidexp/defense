"""
Defense base game entry point.
"""

from typing import Dict, Set, Tuple, List, Any, Optional
import math
import os
import pytmx
import yaml
from beer.event import KeyCode, get_key_state
from beer.sprite import Sheet, Sprite
from beer.texture import Texture

SPRITES = []

KEYS: Set[KeyCode] = set()

MAP: Any = None


class Mob:

    speed: float

    def __init__(self, sprite: Sprite, speed: float) -> None:
        self.__sprite = sprite
        self.__dst_x = sprite.x
        self.__dst_y = sprite.y
        self.__time_acc = 0.0
        self.speed = speed

    @property
    def destination(self) -> Tuple[float, float]:
        return (self.__dst_x, self.__dst_y)

    @destination.setter
    def destination(self, dst: Tuple[int, int]) -> None:
        self.__dst_x, self.__dst_y = dst

    @property
    def is_moving(self) -> bool:
        return self.__sprite.x != self.__dst_x or self.__sprite.y != self.__dst_y

    def update(self, dt: float) -> None:
        if not self.is_moving:
            self.__time_acc = 0.0
            return

        self.__time_acc += dt
        t = 1.0 / self.speed

        while self.__time_acc >= t:
            dx = self.__dst_x - self.__sprite.x
            if math.fabs(dx) > 0:
                dx = math.copysign(1, dx)

            dy = self.__dst_y - self.__sprite.y
            if math.fabs(dy) > 0:
                dy = math.copysign(1, dy)

            self.__sprite.x += dx
            self.__sprite.y += dy
            self.__time_acc -= dt


CHARACTER: Optional[Mob] = None


def load_map(tiled_map_filename: str) -> None:
    global MAP  # pylint: disable=global-statement

    tiled_map = pytmx.TiledMap(tiled_map_filename)

    sheet_tiles: Dict[str, List[Tuple[int, int, int, int]]] = {}

    for filename, rect, _ in (spec for spec in tiled_map.images if spec is not None):
        sheet_tiles.setdefault(filename, []).append(rect)

    sheet_textures = {
        filename: Texture(filename) for filename in sheet_tiles
    }

    sheets = {
        filename: Sheet(sheet_textures[filename], sheet_tiles[filename])
        for filename in sheet_tiles
    }

    for layer in tiled_map.layers:
        for x, y, (filename, rect, _) in layer.tiles():
            sprite = Sprite(sheets[filename])
            sprite.frame = sheet_tiles[filename].index(rect)
            sprite.x = x * tiled_map.tilewidth
            sprite.y = y * tiled_map.tileheight
            sprite.visible = True
            SPRITES.append(sprite)

    MAP = tiled_map

    print(f'Map {tiled_map_filename} loaded')


def load_character(character_filename: str) -> None:
    global CHARACTER  # pylint: disable=global-statement

    with open(character_filename, 'r') as file_handle:
        data = yaml.load(file_handle)
        spr_info = data['sprite']
        texture_filename = os.path.join(os.path.dirname(character_filename), spr_info['sheet'])
        texture = Texture(texture_filename)
        rect = spr_info['x'], spr_info['y'], spr_info['w'], spr_info['h']
        sheet = Sheet(texture, [rect])
        sprite = Sprite(sheet)
        sprite.visible = True
        SPRITES.append(sprite)

        # place the character on the spawn point
        spawn_x, spawn_y = [int(coord) for coord in MAP.properties.get('spawn_point', '0,0').split(',')]
        sprite.x = MAP.tilewidth * spawn_x
        sprite.y = MAP.tileheight * spawn_y

        CHARACTER = Mob(sprite, 16)


def init() -> None:
    load_map('game/defense/maps/01_demo.tmx')
    load_character('game/defense/characters/rob.yaml')

    print('Defense initialized')


def update(delta_time: float) -> None:
    global KEYS, MAP, CHARACTER  # pylint: disable=global-statement
    current_keys = {code for code in KeyCode if get_key_state(code).pressed}
    for pressed in current_keys - KEYS:
        print(f'{pressed.name} pressed!')
    for released in KEYS - current_keys:
        print(f'{released.name} released!')
    KEYS = current_keys

    if CHARACTER:
        if not CHARACTER.is_moving:
            tw = MAP.tilewidth
            th = MAP.tileheight
            dst_x, dst_y = CHARACTER.destination

            if KeyCode.W in KEYS:
                dst_y -= th
            elif KeyCode.S in KEYS:
                dst_y += th
            elif KeyCode.A in KEYS:
                dst_x -= tw
            elif KeyCode.D in KEYS:
                dst_x += tw

            dst = (dst_x, dst_y)
            if CHARACTER.destination != dst:
                CHARACTER.destination = dst

        CHARACTER.update(delta_time)

def fini() -> None:
    print('Defense finalized')
