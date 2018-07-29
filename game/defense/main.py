"""
Defense base game entry point.
"""

from typing import Optional, Set

from beer.event import KeyCode, get_key_state
from beer.sprite import Sheet, Sprite
from beer.texture import Texture

SPRITE: Optional[Sprite] = None

KEYS: Set[KeyCode] = set()



KEYS = set()


def init() -> None:
    global SPRITE  # pylint: disable=global-statement
    # example usage of Texture
    filename = 'game/defense/sprites/characters.png'
    tex = Texture(filename)
    print('Loaded {}'.format(filename))
    print('Size: {}x{} ({})'.format(tex.width, tex.height, tex.format))

    frames = ((0, 102, 16, 16),)
    sheet = Sheet(tex, frames)
    SPRITE = Sprite(sheet)
    SPRITE.visible = True
    SPRITE.x = 800 / 2 - 16 / 2
    SPRITE.y = 600 / 2 - 16 / 2

    print('Defense initialized')


def update(delta_time: float) -> None:
    if SPRITE:
        SPRITE.x += delta_time * 10

    global KEYS  # pylint: disable=global-statement
    current_keys = {code for code in KeyCode if get_key_state(code).pressed}
    for pressed in current_keys - KEYS:
        print(f'{pressed.name} pressed!')
    for released in KEYS - current_keys:
        print(f'{released.name} released!')
    KEYS = current_keys


def fini() -> None:
    print('Defense finalized')
