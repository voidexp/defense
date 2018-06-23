#!/usr/bin/env python3

from functools import partial
from itertools import chain
import click
import collections
import pystache as mustache
import os
import platform
import sys
import subprocess as sp


PROJECT_PATH = os.getcwd()


GEN_FILES = {
    'Tuprules.tup.in': 'Tuprules.tup',
}


DYLIB_SUFFIXES = {
    'darwin': 'dylib',
    'linux': 'so',
    'win': 'dll',
}


STLIB_SUFFIXES = {
    'darwin': 'a',
    'linux': 'a',
    'win': 'lib',
}


OBJ_SUFFIXES = {
    'darwin': 'o',
    'linux': 'o',
    'win': 'obj',
}


IS_WINDOWS = sys.platform.startswith('win')
IS_LINUX = sys.platform.startswith('linux')
IS_OSX = sys.platform.startswith('darwin')


def get_platform_file_suffix(suffix_map):
    for k, v in suffix_map.items():
        if sys.platform.startswith(k):
            return v

    raise UnsupportedPlatformError


EXECUTABLE_NAME = '{}-{}'.format(
    os.path.basename(PROJECT_PATH).lower(),
    platform.machine().lower()
)


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


class UnsupportedPlatformError(RuntimeError):

    def __init__(self):
        super(UnsupportedPlatformError, self).__init__('unsupported platform "{}"'.format(sys.platform))


class Config():

    def __init__(self, **kwargs):
        self.executable = kwargs.get('executable', EXECUTABLE_NAME)
        self.project_path = kwargs.get('project_path', PROJECT_PATH)
        self.inc_paths = kwargs.get('inc_paths', {})
        self.lib_paths = kwargs.get('lib_paths', {})
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
            'build_mode': 'debug' if self.debug else 'release',
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
            'obj_suffix': get_platform_file_suffix(OBJ_SUFFIXES),
            'executable': self.executable,
        }

        config.update({'{}_cflags'.format(key): ' '.join(sorted(value)) for key, value in self.cflags.items()})
        config.update({'{}_ldflags'.format(key): ' '.join(sorted(value)) for key, value in self.ldflags.items()})

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
            stlib_link_rule='{path} -Wl,-r -no-pie %f -o %o -nostdlib'.format(path=path),
            cflags=cflags,
            ldflags=ldflags,
            inc_dir_flag='-I{}',
            lib_dir_flag='-L{}',
            lib_flag='-l{}'
        )


def check_msvc(debug):
    cl_path = find_executable('cl.exe')
    link_path = find_executable('link.exe')
    lib_path = find_executable('lib.exe')
    if cl_path and link_path and lib_path:
        if debug:
            cflags = ' /Od /DDEBUG /DEBUG /Zi /FS'
            ldflags = '/DEBUG:FULL'
        else:
            cflags = ''
            ldflags = ''

        return CompilerSpec(
            cc_rule='{path} /TC /nologo /Fo:%o $(CFLAGS) /c %f'.format(path=cl_path),
            link_rule='{path} /NOLOGO /OUT:%o $(LDFLAGS) /SUBSYSTEM:WINDOWS %f'.format(path=link_path),
            dylib_link_rule='{path} /NOLOGO /OUT:%o /IMPLIB:%O.lib /DLL $(LDFLAGS) /SUBSYSTEM:WINDOWS %f'.format(path=link_path),
            stlib_link_rule='{path} /NOLOGO /OUT:%o $(LDFLAGS) /SUBSYSTEM:WINDOWS %f'.format(path=lib_path),
            cflags=cflags,
            ldflags=ldflags,
            inc_dir_flag='/I {}',
            lib_dir_flag='/LIBPATH:{}',
            lib_flag='{}.lib'
        )


COMPILERS = {
    'GCC': check_gcc,
    'MSVC': check_msvc,
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
        ldflags = sp.check_output([pkgconfig, pkg_name, '--libs']).strip().decode('utf8')
        ldflags_set = config.ldflags.setdefault(store_name, set())
        ldflags_set.add(ldflags)

        cflags = sp.check_output([pkgconfig, pkg_name, '--cflags']).strip().decode('utf8')
        cflags_set = config.cflags.setdefault(store_name, set())
        cflags_set.add(cflags)
        return True
    except sp.CalledProcessError:
        return False


def find_lib(config, lib_name, store_name=None):
    lib_filename = '{}.lib'.format(lib_name)
    if store_name is None:
        store_name = lib_name

    for path in config.lib_paths.get(store_name, []):
        for filename in os.listdir(path):
            abs_filename = os.path.join(path, filename)
            if filename == lib_filename and os.path.isfile(abs_filename):
                ldflags = config.ldflags.setdefault(store_name, set())
                ldflags.add(config.compiler_spec.lib_dir_flag.format(path))
                ldflags.add(config.compiler_spec.lib_flag.format(lib_name))
                return True


def find_header(config, header_name, store_name=None):
    if store_name is None:
        store_name = os.path.splitext(os.path.basename())[0]

    for path in config.inc_paths.get(store_name, []):
        for filename in os.listdir(path):
            abs_filename = os.path.join(path, filename)
            if filename == header_name and os.path.isfile(abs_filename):
                cflags = config.cflags.setdefault(store_name, set())
                cflags.add(config.compiler_spec.inc_dir_flag.format(path))
                return True


def find_sdl2(config):
    if IS_WINDOWS:
        libs = ['SDL2', 'SDL2main']
        headers = ['SDL.h']
        return all(chain(
            (find_lib(config, lib, 'sdl') for lib in libs),
            (find_header(config, header, 'sdl') for header in headers)
        ))
    else:
        return find_pkg_config(config, 'sdl2', 'sdl')


def find_python3(config):
    if IS_WINDOWS:
        libs = ['python36']
        headers = ['Python.h']
        return all(chain(
            (find_lib(config, lib, 'python') for lib in libs),
            (find_header(config, header, 'python') for header in headers)
        ))
    else:
        return find_pkg_config(config, 'python-3.6', 'python')


def generate_files(config):
    context = config.as_dict()

    for template_filename, out_filename in GEN_FILES.items():
        with open(template_filename, 'r') as tmpl_fp, open(out_filename, 'w') as out_fp:
            tmpl = tmpl_fp.read()
            makefile = mustache.render(tmpl, context)
            out_fp.write(makefile)


FINDERS = (
    ('C compiler', 'cc', find_compiler),
    ('SDL2', 'sdl', find_sdl2),
    ('Python3', 'python', find_python3),
)


def lib_options(lib_specs):

    def wrapper(func):
        for user_name, lib_name, _ in lib_specs:
            func = click.option(
                '--{}-libpath'.format(lib_name),
                type=click.Path(exists=True, file_okay=False, dir_okay=True),
                multiple=True,
                help='{} library search path'.format(user_name)
            )(func)

            func = click.option(
                '--{}-incpath'.format(lib_name),
                type=click.Path(exists=True, file_okay=False, dir_okay=True),
                multiple=True,
                help='{} headers search path'.format(user_name)
            )(func)

        return func

    return wrapper


@click.command()
@click.option('--executable', type=str, default=EXECUTABLE_NAME,
              help='output executable (default: "{}")'.format(EXECUTABLE_NAME))
@lib_options(FINDERS)
def configure(executable, **kwargs):
    """Configures the project and creates the building configuration."""

    def get_paths(suffix):
        return {
            key.replace(suffix, ''): path for key, path in kwargs.items()
            if key.endswith(suffix)
        }

    inc_paths = get_paths('_incpath')
    lib_paths = get_paths('_libpath')

    config = Config(inc_paths=inc_paths, lib_paths=lib_paths)
    config.executable = executable

    for name, _, find_func in FINDERS:
        print('Checking for {}...'.format(name), end=' ')
        result = find_func(config)
        if result:
            if isinstance(result, bool):
                print('found')
            else:
                print(result)
        else:
            print('not found')
            print('Abort')
            exit(1)

    generate_files(config)


if __name__ == '__main__':
    configure()
