import logging
import typing

from ..tab import Tab
from ..util import iter_config_dirs, iter_modules_from_dir

logger = logging.getLogger(__name__)

_modules = []  # Fixes missing Filters tab due to lost reference on PySide6

for dir in iter_config_dirs('tabs'):
    for module in iter_modules_from_dir(dir, 'efck.tabs.'):
        _modules.append(module)

# Export tabs here.
# Import `from .tabs` to avoid double import of the module
# (our relative imports and our `import_module_from_file()`
# above are apparently treated differently).
globals().update({cls.__name__: cls for cls in Tab.__subclasses__()})
# And for IDE ...
if typing.TYPE_CHECKING:
    from .emoji import EmojiTab  # noqa: F401
