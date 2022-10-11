# -*- mode: python ; coding: utf-8 -*-
"""
Run from project root with:
$ pyinstaller packaging/pyinstaller.spec
"""
import glob
import os
import sys
import typing
from itertools import chain
from pprint import pprint
from tempfile import NamedTemporaryFile

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

if typing.TYPE_CHECKING:
    from PyInstaller.building.api import COLLECT, EXE, MERGE, PYZ  # noqa: F401
    from PyInstaller.building.build_main import Analysis  # noqa: F401
    from PyInstaller.building.datastruct import TOC, Target, Tree  # noqa: F401
    from PyInstaller.building.osx import BUNDLE  # noqa: F401
    from PyInstaller.building.splash import Splash  # noqa: F401

from efck import qApp

APP_NAME = qApp.applicationName()
assert ' ' not in APP_NAME, APP_NAME
ICON_FILE = os.path.join('..', 'efck', 'icons', 'logo.png')

_locals = {}
with open(os.path.join('efck', '_version.py')) as version_file, \
        open(os.path.join('packaging', 'win', 'pyi-win-version.rc.in')) as template, \
        NamedTemporaryFile('w+', delete=False) as win_version_file:
    exec(version_file.read(), _locals)
    VERSION = _locals['__version__']
    win_version_file.write(template.read().format(version=VERSION))

datas = collect_data_files(
    'efck',
    excludes=[
        '.gitignore',
        '*/README.md',
        '**/*.c',
        '**/*.so',
    ],
)
assert datas
datas += [(os.path.abspath(i), '.')
          for i in chain(glob.glob('packaging/debian/*.svg'),
                         glob.glob('packaging/debian/*.desktop'))]

block_cipher = None
a = Analysis(
    ['../run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        *collect_submodules('efck.tabs'),
        *collect_submodules('efck.filters'),
        # 'pdb',  # For debugging with breakpoint(). Disable in prod.
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6',
        'shiboken6',
        'PyQt5',
        'qtpy',
        'efck._qt.pyside6',
        'efck._qt.pyqt5',
        'efck._qt.qtpy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# DO NOT remove system libs
#
prev_binaries = set(a.binaries)
if sys.platform in ('linux', 'darwin'):
    a.exclude_system_libraries(list_of_exceptions=[])  # glob expression
print('\n\nSTRIPPED SYSTEM LIBS')
pprint(sorted(set(prev_binaries) - set(a.binaries)))

# Strip PyQt6 translations (5 MB)
assert any(i for i in a.datas if 'translations' in i[0])
a.datas = [i for i in a.datas if 'translations' not in i[0]]

# Report Analysis
for key in (
        'binaries',
        'datas',
        'pure',
        'scripts',
):
    print(f'\n\n{key.upper()}')
    pprint(sorted(getattr(a, key)))
    print()

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name=APP_NAME,
    icon=ICON_FILE,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=win_version_file.name,
)
os.remove(win_version_file.name)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=APP_NAME,
)

app = BUNDLE(
    coll,
    name=f'{APP_NAME.title().replace("-", " ")}.app',
    icon=ICON_FILE,
    bundle_identifier=None,
    version=VERSION,
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode in macOS<10.14
        'NSAppleScriptEnabled': True,  # Allows this app to be AppleScript-able
        'NSAppleEventsUsageDescription': 'Efck chat keyboard needs to be able '
                                         'to type into the previously focused window.',
    },
)
