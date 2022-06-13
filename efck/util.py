import os
from contextlib import contextmanager
from importlib.machinery import ModuleSpec, SourceFileLoader
from importlib.util import module_from_spec
from pathlib import Path

from . import CONFIG_DIRS


@contextmanager
def chdir(path):
    prev_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev_cwd)


def import_module(module_name, path):
    path = os.path.abspath(path)
    loader = SourceFileLoader(module_name, path)
    module = module_from_spec(ModuleSpec(module_name, loader, origin=path))
    loader.exec_module(module)
    return module


def iter_config_dirs(subdir):
    assert subdir
    yield Path(__file__).parent / subdir
    for dir in reversed(CONFIG_DIRS):
        path = Path(dir) / subdir
        if path.exists():
            yield path
