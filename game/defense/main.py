"""
Defense base game entry point.
"""

import time
from beer.texture import Texture
from beer.sprite import Sheet
from beer.sprite import Sprite
from beer.event import get_key_state
from beer.event import KeyCode


sprite = None

keys = {code: False for code in KeyCode}


def init():
    # example usage of Texture
    filename = 'game/defense/sprites/characters.png'
    tex = Texture(filename)
    print('Loaded {}'.format(filename))
    print('Size: {}x{} ({})'.format(tex.width, tex.height, tex.format))

    frames = ((0, 102, 16, 16),)
    sheet = Sheet(tex, frames)
    global sprite
    sprite = Sprite(sheet)
    sprite.visible = True
    sprite.x = 800 / 2 - 16 / 2
    sprite.y = 600 / 2 - 16 / 2

    print('Defense initialized')


def update(dt):
    sprite.x += dt * 10

    global keys
    current_keys = {code: get_key_state(code).pressed for code in KeyCode}
    for code in KeyCode:
        if current_keys[code] != keys[code]:
            state = 'pressed' if current_keys[code] else 'released'
            keys[code] = current_keys[code]
            print(f'{code.name} key {state}')

def fini():
    print('Defense finalized')
