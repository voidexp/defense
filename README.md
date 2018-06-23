Defense - a toy project 2D game
===============================
[![Build status](https://ci.appveyor.com/api/projects/status/kooq7i56g265xo9y?svg=true)](https://ci.appveyor.com/project/V0idExp/defense) [![Build Status](https://travis-ci.org/V0idExp/defense.svg?branch=master&label=Linux)](https://travis-ci.org/V0idExp/defense)

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

* Python 3 (version 3.6.5✔)
* C compiler with C99 standard support
* [tup](http://gittup.org/tup/) build tool
* pkg-config (for Linux/OSX library discover)
* SDL2 development library (version 2.0.8✔)

## Create and setup Python virtual environment
Python3 `venv` module is used to create a bottled virtual environment to avoid
messing the global one with project-specific packages.

    python3 -m venv .env

By "activating" it, a number of shell variables will be overridden such a way
that the local Python interpreter will be used and not the system one.

On Linux/OSX if using Bash:

    source .env/bin/activate

On Windows in CMD/PowerShell

    .env\Scripts\activate

Install the build-environment packages:

    pip install -r requirements.txt

_NOTE: these packages are required by build scripts._

Install the game runtime packages into engine's directory:

    pip install -t core/beer/python requirements-game.txt

_NOTE: these packages are available to game's Python runtime for import, add
there anything you'd need._

## Compile the engine
First, run the `configure.py` script which will attempt to find the compiler,
libraries and whatever is needed and generate build rules:

On Linux/OSX:

    python configure.py

On Windows you have to specify explicitly the paths to development headers and
libraries using command-line options, for example:

    python configure.py --sdl-incpath=C:\SDKs\SDL2-2.0.8\include --sdl-libpath=C:\SDKs\SDL2-2.0.8\lib\x64 --python-incpath=C:\Python36\include --python-libpath=C:\Python36\libs

For additional options and their meanings, check

    python configure.py --help

The build command is the simplest one, assuming you have `tup` in system PATH:

    tup


# Play!
On successful build, you will have the game executable placed in `core/`,
however, it may be necessary to specify also the library paths before runnning
it, otherwise the loader won't be able to resolve missing DLLs:

Linux/OSX example:

    LD_LIBRARY_PATH=core/beer core/defense-x86_64

Windows example:

    set PATH=%PATH%;core/beer;C:\SDKs\SDL2-2.0.8\lib\x64;C:\Python36
    core/defense-amd64.exe

NOTE: On Windows you can also copy-paste the required DLLs right into the
directory where the executable is located.
