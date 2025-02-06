import logging
import re
from pathlib import Path

try:
    import unicodedata2 as unicodedata
except ImportError:
    # Maybe unicodedata2 is not available, e.g.
    # as python3-unicodedata2 package on an older Debian
    import unicodedata

logger = logging.getLogger(__name__)
logger.info('Using unicodedata %s', unicodedata.unidata_version)

EMOJI_ORDERING_FILE = Path(__file__).parent / 'emoji-ordering.txt'
# Alt keywords as used in GitHub, Trac, Redmine, Trello, Zendesk, Slack,
# Discourse, Discord, Bitbucket, Gitter, YouTube, Mattermost ...
EMOJI_SHORTCODES_FILE = Path(__file__).parent / 'emoji-shortcodes.txt'


def enum_emojis():
    from .config import config_state, _skin_tone
    from .tabs.emoji import EmojiTab
    from .util import iter_config_dirs

    # Invert emoji filters from options
    should_skip_emoji = {k for filters in config_state[EmojiTab.__name__].values()
                         for k, is_enabled in filters.items()
                         if not is_enabled}
    should_skip_emoji = re.compile(fr'(?:^|(?:[:,] ))\b(?:{"|".join(should_skip_emoji)})').search

    # Load GitHub/Slack emoji shortcodes
    with open(EMOJI_SHORTCODES_FILE, encoding='utf-8') as fd:
        shortcodes = dict(line.rstrip().split(maxsplit=1)
                          for line in fd)

    # Load custom emoji strings
    custom_strings = {}
    for dir in iter_config_dirs('.'):
        file = dir / 'emoji-custom-strings.txt'
        if file.exists():
            with open(file, encoding='utf-8') as fd:
                custom_strings.update(line.split(maxsplit=1)
                                      for line in (line.strip() for line in fd)
                                      if line and not line.startswith('#'))

    # Chars present in the ordering file but not in the shortcodes file
    MODIFIER_CHARS = (
        '\N{ZERO WIDTH JOINER}',      # joins some emojis, like pirate-ZWJ-flag
        '\N{VARIATION SELECTOR-15}',  # variation selector "text"
        '\N{VARIATION SELECTOR-16}',  # variation selector "emoji" with color
    )
    STOP_WORDS = (
        'a',
        'and',
        'in',
        'of',
        'on',
        'the',
        'with',
    )

    def clean_desc(text):
        text = re.sub(fr'({"|".join(_skin_tone)})', '', text)
        text = re.sub(fr'\b({"|".join(STOP_WORDS)})\b', '', text)
        text = re.sub(r'\W{2,}', ' ', text)
        return text

    emojis = []
    known_man_names = set()

    official_emoji = set()
    with open(EMOJI_ORDERING_FILE, encoding='utf-8') as fd:
        for line in fd:
            if line.startswith('#'):
                continue

            seq, unicode_version, emoji, name = re.match(r'(.+?) ; (.+?) # ([^ ]+) (.+)', line).groups()
            official_emoji.add(emoji)

            # Temporary workaround for country flags
            name = name.lower()

            try:
                alt_name = unicodedata.name(emoji, '').lower()
                if alt_name == name:
                    alt_name = ''
            except (TypeError, SyntaxError):
                alt_name = ''

            emoji_normed = ''.join(ch for ch in emoji if ch not in MODIFIER_CHARS)
            shortcode = shortcodes.pop(emoji_normed, '')

            if name.startswith('man'):
                known_man_names.add(name.split(':')[0])
            if should_skip_emoji(name):
                continue

            name = clean_desc(name)
            alt_name = clean_desc(alt_name)
            shortcode = clean_desc(shortcode)
            custom_str = ' '.join(filter(None, (custom_strings.get(ch, '') for ch in emoji)))

            emojis.append((emoji, name, alt_name, shortcode, custom_str))

    # All shortcodes were consumed
    assert not shortcodes, shortcodes

    # Trail with custom emoji sequences from the file
    for custom_emoji in custom_strings.keys() - official_emoji:
        emojis.append((custom_emoji, '', '', '', custom_strings[custom_emoji]))

    # Skip person in case of emojis for which either man or woman
    # versions also exist ("health worker", "astronout" ...)
    is_person_disabled = not config_state[EmojiTab.__name__]['Gender']['person']
    if is_person_disabled:
        emojis[:] = [i for i in emojis if f'man {i[1]}' not in known_man_names]
    return emojis
