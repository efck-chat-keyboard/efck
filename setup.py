import os
from pathlib import Path

from setuptools import setup, find_packages


if __name__ == '__main__':
    kwargs = {}
    version_file = Path('efck') / '_version.py'
    if Path(__file__).with_name('.git').is_dir():
        kwargs['use_scm_version'] = {'write_to': version_file}
    elif version_file.is_file():
        _locals = {}
        exec(open(version_file).read(), _locals)
        kwargs['version'] = _locals['__version__']

    setup(
        name='efck',
        description="Emoji filter / Unicode chat keyboard",
        license='AGPL-3.0',
        url='https://efck-chat-keyboard.github.io/',
        project_urls={
            'Source': 'https://github.com/efck-chat-keyboard/efck',
            'Tracker': 'https://github.com/efck-chat-keyboard/efck/issues',
        },
        long_description=open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8').read(),
        long_description_content_type='text/markdown',
        packages=find_packages(),
        include_package_data=True,
        setup_requires=[
            'setuptools_git',
            'setuptools_scm',
        ],
        install_requires=[
        ],
        extras_require={
            'doc': [
            ],
            'dev': [
                'flake8',
                'coverage',
                'pyinstaller == 6.9',
                'pillow',   # for pyinstaller
            ],
            'extra': [
                'unicodedata2',
            ]
        },
        entry_points={
            'gui_scripts': [
                'efck-chat-keyboard = efck.__main__:main',
            ]
        },
        test_suite="efck.tests",
        python_requires='>=3.7',
        author='Nono Viamoto',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: Customer Service',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Adaptive Technologies',
            'Topic :: Communications :: Chat',
            'Topic :: Communications :: Email',
            'Topic :: Text Processing :: Filters',
        ],
        **kwargs,
    )
