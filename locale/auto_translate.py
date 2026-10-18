import json
import pathlib
import time
import urllib.parse
import urllib.request

import polib

BASE = pathlib.Path(__file__).parent

LOCALES = {
    'zh_Hant': 'zh-TW',
    'en_US': 'en-US',
    'en_GB': 'en-GB',
    'en_AU': 'en-AU',
    'de': 'de',
    'ja': 'ja',
    'es': 'es',
    'pt': 'pt',
    'fr': 'fr',
}

API_URL = 'https://api.mymemory.translated.net/get'


def translate(text: str, target: str) -> str | None:
    params = {
        'q': text,
        'langpair': f'zh-CN|{target}',
    }
    url = API_URL + '?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if data.get('responseStatus') == 200:
            return data['responseData']['translatedText']
    except Exception:
        return None
    return None


def main():
    for locale, target in LOCALES.items():
        po_path = BASE / locale / 'LC_MESSAGES' / 'django.po'
        if not po_path.exists():
            print(f'Missing {po_path}')
            continue
        po = polib.pofile(str(po_path))
        updated = 0
        for entry in po:
            if entry.msgstr:
                continue
            if locale == 'zh_Hant':
                # For Traditional Chinese, use MyMemory zh-CN|zh-TW
                result = translate(entry.msgid, target)
            else:
                result = translate(entry.msgid, target)
            if result is not None:
                entry.msgstr = result
                updated += 1
                print(f'[{locale}] {entry.msgid!r} -> {result!r}')
            else:
                print(f'[{locale}] FAILED {entry.msgid!r}')
            time.sleep(0.15)
        po.save()
        print(f'Saved {locale} ({updated} updated)')


if __name__ == '__main__':
    main()
