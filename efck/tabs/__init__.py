import logging
import typing
from glob import glob
from pathlib import Path

from ..tab import Tab
from ..util import import_pyinstaller_bundled_submodules, iter_config_dirs, import_module_from_file

logger = logging.getLogger(__name__)

_modules = []  # Fixes missing Filters tab due to lost reference on PySide6

_modules.extend(import_pyinstaller_bundled_submodules(__name__))

for dir in iter_config_dirs('tabs'):
    for file in sorted(glob(str(dir / '*.py*'))):
        basename = Path(file).stem
        if basename.startswith('_'):
            continue
        logger.debug('Loading tab "%s"', file)
        module = import_module_from_file(f'efck.tabs.{basename}', file)
        _modules.append(module)

# Export tabs here.
# Import `from .tabs` to avoid double import of the module
# (our relative imports and our `import_module_from_file()`
# above are apparently treated differently).
globals().update({cls.__name__: cls for cls in Tab.__subclasses__()})
# And for IDE ...
if typing.TYPE_CHECKING:
    from .emoji import EmojiTab  # noqa: F401
