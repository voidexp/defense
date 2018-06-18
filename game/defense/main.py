"""
Defense base game entry point.
"""

from beer.texture import Texture  # pylint: disable=import-error


def init():
    # example usage of Texture
    tex = Texture()
    print('Defense initialised')


def fini():
    print('Defense finalized')
