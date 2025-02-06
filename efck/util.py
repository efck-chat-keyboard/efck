import importlib.util
import logging
import pkgutil
from pathlib import Path

from . import CONFIG_DIRS

logger = logging.getLogger(__name__)


def iter_modules_from_dir(dir: str, prefix: str):
    for modinfo in pkgutil.iter_modules([dir], prefix=prefix):
        spec = modinfo.module_finder.find_spec(modinfo.name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module


def iter_config_dirs(subdir):
    assert subdir
    yield Path(__file__).parent / subdir
    for dir in reversed(CONFIG_DIRS):
        path = Path(dir) / subdir
        if path.is_dir():
            yield path
