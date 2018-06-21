Defense - a toy project 2D game
===============================
Just another tower defense game which is badly designed, implemented and by all
means is a waste of time, except that it is made for fun, learning and trying
out new (to me) technologies, concepts and tricks.

The game is built on top of a custom C engine and all the logic and the actual
game code is written in Python.

Try it out, fork it, hack it, and if you enjoy any part of it, let me know! :)

![latest screenshot](/screenshot.png?raw=true)


# Build instructions
The C engine has to be compiled, and there is a number of tools and libraries
needed:

* Python 3 interpreter and development headers
* pip for Python 3
* GCC compiler
* [tup](http://gittup.org/tup/) build tool
* pkg-config (available on every UNIX flavor)
* SDL2 library and development headers

## Create and setup Python virtual environment
Python3 `venv` module is used to create a bottled virtual environment to avoid
messing the global one with project-specific packages.

    $ python3 -m venv .env
    $ . .env/bin/activate       # for Bash shell
    $ . .env/bin/activate.fish  # for Fish shell (my preference)

Install the build-environment packages:

    $ pip install -r requirements.txt

_NOTE: these packages are required by build scripts._

Install the game runtime packages into engine's directory:

    $ pip install -t core/beer/python requirements-game.txt

_NOTE: these packages are available to game's Python runtime for import, add
there anything you'd need._

## Compile the engine's core
First, run the `configure.py` script which will attempt to find the compiler,
libraries and whatever is needed and generate build rules:

    $ ./configure.py

The build command is the simplest one, assuming you have `tup` installed:

    $ tup


# Play!
On successful build, you will have a `defense-x86_64` executable (on 64-bit
architecture) in the project's root directory, just execute it:

    $ ./defense-x86_64

