"""
Defense base game entry point.
"""

from typing import Dict, Set, Tuple, List, Any, Optional

import os
import pytmx
import yaml
from beer.event import KeyCode, get_key_state
from beer.sprite import Sheet, Sprite
from beer.texture import Texture

SPRITES = []

KEYS: Set[KeyCode] = set()

CHARACTER: Optional[Sprite] = None

MAP: Any = None


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


def init() -> None:
    load_map('game/defense/maps/01_demo.tmx')
    load_character('game/defense/characters/rob.yaml')

    print('Defense initialized')


def update(delta_time: float) -> None:
    global KEYS  # pylint: disable=global-statement
    current_keys = {code for code in KeyCode if get_key_state(code).pressed}
    for pressed in current_keys - KEYS:
        print(f'{pressed.name} pressed!')
    for released in KEYS - current_keys:
        print(f'{released.name} released!')
    KEYS = current_keys


def fini() -> None:
    print('Defense finalized')
