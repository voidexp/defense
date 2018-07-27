from _beer import lib, ffi  # pylint: disable=import-error,no-name-in-module
from enum import IntEnum
from enum import unique


@unique
class KeyCode(IntEnum):

    W = lib.BEER_KEY_W
    A = lib.BEER_KEY_A
    S = lib.BEER_KEY_S
    D = lib.BEER_KEY_D
    ESC = lib.BEER_KEY_ESC
    SPACE = lib.BEER_KEY_SPACE


class KeyState:

    pressed: bool

    def __init__(self, pressed):
        self.pressed = pressed


def get_key_state(code: KeyCode) -> KeyState:
    state = ffi.new('struct BeerKeyState*')
    if lib.beer_key_get_state(code, state) != lib.BEER_OK:
        raise RuntimeError(f'invalid key {code}')
    return KeyState(state.pressed)

