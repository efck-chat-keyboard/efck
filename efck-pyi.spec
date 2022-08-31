"""
efck PyInstaller spec file

Build with:
$ pyinstaller efck.spec
"""
import typing
from pprint import pprint

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

if typing.TYPE_CHECKING:
    from PyInstaller.building.api import COLLECT, EXE, MERGE, PYZ
    from PyInstaller.building.build_main import Analysis
    from PyInstaller.building.datastruct import TOC, Target, Tree
    from PyInstaller.building.osx import BUNDLE
    from PyInstaller.building.splash import Splash


block_cipher = None
# pprint(collect_data_files('efck'))
# pprint(collect_data_files('efck', include_py_files=True, includes=['*.py', '*/*.py']))
# pprint(collect_data_files('efck.tabs', include_py_files=True, includes=['*.py']))
# asd
a = Analysis(
    ['run.py',

     # *[i[0] for i in collect_data_files('efck', include_py_files=True, includes=['*.py', '*/*.py'])],
     ],
    pathex=[],
    binaries=[],
    datas=[
        *collect_data_files('efck', excludes=['.gitignore', '*/README.md',
                                              '**/*.c', '**/*.so']),
    ],
    hiddenimports=[
        # 'efck',
        *collect_submodules('efck.tabs'),
        *collect_submodules('efck.filters'),
        # 'pdb',  # For debugging with breakpoint(). Disable in prod.
        # *collect_submodules('efck'),
        # *collect_submodules('efck._qt'),
        # *collect_submodules('PyQt6.QtCore'),
        # *collect_submodules('PyQt6.QtGui'),
        # *collect_submodules('PyQt6.QtWidgets'),
        # *collect_submodules('PyQt6.QtNetwork'),
        # *collect_submodules('PyQt6.QtTest'),
        # 'json', 'glob',

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

        'email',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# DO NOT remove system libs
#
prev_binaries = set(a.binaries)
import sys
if sys.platform in ('linux', 'darwin'):
    a.exclude_system_libraries(list_of_exceptions=[])  # glob expression
print('\n\nSTRIPPED SYSTEM LIBS')
pprint(sorted(set(prev_binaries) - set(a.binaries)))

# Strip Qt translations (5 MB)
assert any(i for i in a.datas if '/translations/' in i[0])
a.datas = [i for i in a.datas if '/translations/' not in i[0]]

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
    name='efck-chat-keyboard.run',
    icon='efck/icons/logo.png',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='efck-chat-keyboard',
)

from efck import __version__

app = BUNDLE(
    coll,
    name='efck-chat-keyboard.app',
    icon='efck/icons/logo.png',
    bundle_identifier=None,
    version=__version__,
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        # 'NSAppleScriptEnabled': True,
        # 'CFBundleShortVersionString': __version__,
    },
)
