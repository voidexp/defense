#!/usr/bin/env python3

from functools import partial
import click
import collections
import pystache as mustache
import os
import platform
import sys
import subprocess as sp


PROJECT_PATH = os.getcwd()
EXECUTABLE_NAME = '{}-{}'.format(os.path.basename(PROJECT_PATH).lower(), platform.machine())


GEN_FILES = {
    'Tuprules.tup.in': 'Tuprules.tup',
}


CompilerSpec = collections.namedtuple(
    'CompilerSpec',
    (
        'cc_rule',
        'link_rule',
        'dylib_link_rule',
        'stlib_link_rule',
        'cflags',
        'ldflags',
        'inc_dir_flag',
        'lib_dir_flag',
        'lib_flag',
    )
)


DYLIB_SUFFIXES = {
    'darwin': 'dylib',
    'linux': 'so',
}


STLIB_SUFFIXES = {
    'darwin': 'a',
    'linux': 'a',
}


class UnsupportedPlatformError(RuntimeError):

    def __init__(self):
        super(UnsupportedPlatformError, self).__init__('unsupported platform "{}"'.format(sys.platform))


def get_platform_file_suffix(suffix_map):
    for k, v in suffix_map.items():
        if sys.platform.startswith(k):
            return v

    raise UnsupportedPlatformError


class Config():

    def __init__(self, **kwargs):
        self.executable = kwargs.get('executable', EXECUTABLE_NAME)
        self.project_path = kwargs.get('project_path', PROJECT_PATH)
        self.debug = kwargs.get('debug', True)
        self.compiler_spec = None
        self.objects = []
        self.deps = []
        self.cflags = {}
        self.ldflags = {}

    def as_dict(self):

        def expand_flag(fmtstr, arg):
            return fmtstr.format(arg)

        config = {
            'project_path': self.project_path,
            'cc_rule': self.compiler_spec.cc_rule,
            'link_rule': self.compiler_spec.link_rule,
            'dylib_link_rule': self.compiler_spec.dylib_link_rule,
            'dylib_suffix': get_platform_file_suffix(DYLIB_SUFFIXES),
            'stlib_link_rule': self.compiler_spec.stlib_link_rule,
            'cflags': self.compiler_spec.cflags,
            'ldflags': self.compiler_spec.ldflags,
            'inc_dir_flag': partial(expand_flag, self.compiler_spec.inc_dir_flag),
            'lib_dir_flag': partial(expand_flag, self.compiler_spec.lib_dir_flag),
            'lib_flag': partial(expand_flag, self.compiler_spec.lib_flag),
            'stlib_suffix': get_platform_file_suffix(STLIB_SUFFIXES),
            'executable': self.executable,
        }

        config.update({'{}_cflags'.format(key): value for key, value in self.cflags.items()})
        config.update({'{}_ldflags'.format(key): value for key, value in self.ldflags.items()})

        return config


def find_executable(executable, path=None):
    """
    Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if os.name == 'os2':
        (base, ext) = os.path.splitext(executable)
        # executable files on OS/2 can have an arbitrary extension, but
        # .exe is automatically appended if no dot is present in the name
        if not ext:
            executable = executable + ".exe"
    elif sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None


def check_gcc(debug):
    path = find_executable('gcc')
    if path:
        cflags = '-Wall -Werror -Wextra -std=c99 -pedantic'
        ldflags = ''
        if debug:
            cflags = cflags + ' -g -DDEBUG'
        else:
            cflags = cflags + ' -O3'

        return CompilerSpec(
            cc_rule='{path} $(CFLAGS) -fPIC -c %f -o %o'.format(path=path),
            link_rule='{path} $(LDFLAGS) %f -o %o'.format(path=path),
            dylib_link_rule='{path} $(LDFLAGS) -shared -Wl,--no-undefined %f -o %o'.format(path=path),
            stlib_link_rule='gcc -Wl,-r -no-pie %f -o %o -nostdlib'.format(path=path),
            cflags=cflags,
            ldflags=ldflags,
            inc_dir_flag='-I{}',
            lib_dir_flag='-L{}',
            lib_flag='-l{}'
        )


COMPILERS = {
    'GCC': check_gcc
}


def find_compiler(config):
    for name, find_func in COMPILERS.items():
        spec = find_func(config.debug)
        if spec is not None:
            config.compiler_spec = spec
            return name
    return False


def find_pkg_config(config, pkg_name, store_name=None):
    pkgconfig = find_executable('pkg-config')
    if pkgconfig is None:
        return False

    store_name = store_name or pkg_name

    try:
        cflags = sp.check_output([pkgconfig, pkg_name, '--cflags']).strip()
        ldflags = sp.check_output([pkgconfig, pkg_name, '--libs']).strip()
        config.cflags[store_name] = cflags
        config.ldflags[store_name] = ldflags
        return True
    except sp.CalledProcessError:
        return False


def generate_files(config):
    context = config.as_dict()

    for template_filename, out_filename in GEN_FILES.items():
        with open(template_filename, 'r') as tmpl_fp, open(out_filename, 'w') as out_fp:
            tmpl = tmpl_fp.read()
            makefile = mustache.render(tmpl, context)
            out_fp.write(makefile)


FINDERS = (
    ('C compiler', find_compiler),
    ('SDL2', partial(find_pkg_config, pkg_name='sdl2', store_name='sdl')),
    ('SDL2_image', partial(find_pkg_config, pkg_name='SDL2_image', store_name='sdl_image')),
    ('Python3', partial(find_pkg_config, pkg_name='python3', store_name='python')),
)


@click.command()
@click.option('--executable', type=str, default=EXECUTABLE_NAME,
              help='target executable name (default: "{}")'.format(EXECUTABLE_NAME))
def configure(executable):
    """Configures the project and creates the building configuration."""
    config = Config()
    config.executable = executable

    for name, find_func in FINDERS:
        print('Checking for {}...'.format(name), end=' ')
        result = find_func(config)
        if result:
            if isinstance(result, bool):
                print('found')
            else:
                print(result)
        else:
            print('not found')
            exit(1)

    generate_files(config)


if __name__ == '__main__':
    configure()
