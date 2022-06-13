import json
import logging
import os
from pathlib import Path

from .tabs.emoji import EmojiTab

logger = logging.getLogger(__name__)

_skin_tone = {
    'light skin tone': 0,
    'medium-light skin tone': 0,
    'medium skin tone': 0,
    'medium-dark skin tone': 0,
    'dark skin tone': 0,
}
_hair_style = {
    'red hair': 1,
    'curly hair': 1,
    'white hair': 1,
    'bald': 1,
    'blond': 1,
}
_gender = {
    'person': 1,
    'man': 0,
    'woman': 0,
}
_emoji_filters = {
    'Skin': _skin_tone,
    'Hair': _hair_style,
    'Gender': _gender,
}
# Global config object. This object in this module is updated and queried and synced with options.
config_state = {
    'selected_tab': 0,
    'window_geometry': [300, 330],
    'zoom': 100,
    EmojiTab.__name__: _emoji_filters,
}


def load_config():
    from . import CONFIG_DIRS

    obj = None
    assert CONFIG_DIRS, CONFIG_DIRS
    for dir_path in CONFIG_DIRS:
        try:
            with open(Path(dir_path) / 'config.json', encoding='utf-8') as fd:
                try:
                    obj = json.load(fd)
                    logger.info('Loading config "%s"', fd.name)
                    break
                except json.JSONDecodeError as e:
                    logger.warning('Error decoding config JSON: %s', e)
        except OSError as e:
            logger.info('Error opening config file: %s', e)
            continue
    if obj:
        logger.info('User config: %s', obj)
    else:
        logger.info('No prior config file. Will use built-in defaults.')
    config_state.update(obj or {})


def dump_config():
    from . import CONFIG_DIRS

    success = False
    for dir_path in CONFIG_DIRS:
        try:
            os.makedirs(dir_path, exist_ok=True)
            with open(Path(dir_path) / 'config.json', 'w', encoding='utf-8') as fd:
                try:
                    json.dump(config_state, fd, indent=2)
                    success = True
                    break
                except Exception as e:
                    logger.warning('Error dumping config: %s', e)
        except OSError as e:
            logger.info('Error opening config file for writing: %s', e)
            continue
    logger.info('Config dumped %ssuccessfully to "%s"', "UN" if not success else "", fd.name)
    return success and fd.name