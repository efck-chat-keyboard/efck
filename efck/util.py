import importlib.util
import logging
import os
from pathlib import Path

from . import CONFIG_DIRS

logger = logging.getLogger(__name__)


def import_module_from_file(module_name, path):
    path = os.path.abspath(path)
    # Should handle all sorts of importable modules (*.py, *.pyc, ...)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def iter_config_dirs(subdir):
    assert subdir
    yield Path(__file__).parent / subdir
    for dir in reversed(CONFIG_DIRS):
        path = Path(dir) / subdir
        if path.is_dir():
            yield path


def import_pyinstaller_bundled_submodules(package):
    # This works with PyInstaller who compiles all our modules into an
    # import-hooked archive rather than keeping non-data files on disk.
    # A few alternatives would be:
    # - Include these submodules in pyinstaller datas (and remove them from PYZ),
    # - List and maintain literal imports
    # This is safe.
    # https://github.com/pyinstaller/pyinstaller/blame/7875d7684c/PyInstaller/loader/pyimod02_importers.py#L115-L117
    modules = []
    if hasattr(__loader__, 'toc'):
        modules = sorted(k for k in __loader__.toc
                         if k.startswith(f'{package}.') and '._' not in k)
        modules = [importlib.import_module(mod) for mod in modules]
    return modules
