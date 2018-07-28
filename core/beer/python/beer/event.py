"""
OS event handling API layer (keyboard, mouse, WM, etc.).
"""
from enum import IntEnum, unique
from _beer import ffi, lib


@unique
class KeyCode(IntEnum):
    """
    List of supported keys.
    """

    W = lib.BEER_KEY_W
    A = lib.BEER_KEY_A
    S = lib.BEER_KEY_S
    D = lib.BEER_KEY_D
    ESC = lib.BEER_KEY_ESC
    SPACE = lib.BEER_KEY_SPACE


class KeyState:
    """
    Keyboard key state.
    """

    pressed: bool

    def __init__(self, pressed):
        self.pressed = pressed


def get_key_state(code: KeyCode) -> KeyState:
    """
    Retrieves the state of a given key.
    """
    state = ffi.new('struct BeerKeyState*')
    if lib.beer_key_get_state(code, state) != lib.BEER_OK:
        raise RuntimeError(f'invalid key {code}')
    return KeyState(state.pressed)
