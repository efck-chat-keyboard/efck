from glob import glob

from ..util import chdir, iter_config_dirs, import_module

_modules = []
for dir in iter_config_dirs('tabs'):
    with chdir(dir):
        for file in glob('*.py'):
            if not file.startswith('_'):
                module = import_module(f'efck.tabs.{file[:-len(".py")]}', file)
                _modules.append(module)  # Fix missing Filters tab due lost reference
