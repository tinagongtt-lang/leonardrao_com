import pathlib

import polib

BASE = pathlib.Path(__file__).parent

PLURAL_FORMS = {
    'zh_Hans': 'nplurals=1; plural=0;',
    'zh_Hant': 'nplurals=1; plural=0;',
    'ja': 'nplurals=1; plural=0;',
    'de': 'nplurals=2; plural=(n != 1);',
    'es': 'nplurals=2; plural=(n != 1);',
    'pt': 'nplurals=2; plural=(n != 1);',
    'fr': 'nplurals=2; plural=(n > 1);',
    'en_US': 'nplurals=2; plural=(n != 1);',
    'en_GB': 'nplurals=2; plural=(n != 1);',
    'en_AU': 'nplurals=2; plural=(n != 1);',
}

for locale, plural in PLURAL_FORMS.items():
    po_path = BASE / locale / 'LC_MESSAGES' / 'django.po'
    po = polib.pofile(str(po_path))
    po.metadata['Plural-Forms'] = plural
    po.metadata['Language'] = locale.replace('_', '-')
    po.save()
    print(f'Fixed header for {locale}')
