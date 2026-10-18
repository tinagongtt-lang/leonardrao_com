import pathlib

import polib

BASE = pathlib.Path(__file__).parent

EXTRA = {
    'zh_Hans': {
        '验证码': '验证码',
        '请输入答案': '请输入答案',
        '你的昵称': '你的昵称',
        '写下你想说的话...': '写下你想说的话...',
        '验证码错误': '验证码错误',
    },
    'zh_Hant': {
        '验证码': '驗證碼',
        '请输入答案': '請輸入答案',
        '你的昵称': '你的暱稱',
        '写下你想说的话...': '寫下你想說的話...',
        '验证码错误': '驗證碼錯誤',
    },
    'en_US': {
        '验证码': 'Verification code',
        '请输入答案': 'Enter the answer',
        '你的昵称': 'Your nickname',
        '写下你想说的话...': 'Write what you want to say...',
        '验证码错误': 'Wrong verification code',
    },
    'en_GB': {
        '验证码': 'Verification code',
        '请输入答案': 'Enter the answer',
        '你的昵称': 'Your nickname',
        '写下你想说的话...': 'Write what you want to say...',
        '验证码错误': 'Wrong verification code',
    },
    'en_AU': {
        '验证码': 'Verification code',
        '请输入答案': 'Enter the answer',
        '你的昵称': 'Your nickname',
        '写下你想说的话...': 'Write what you want to say...',
        '验证码错误': 'Wrong verification code',
    },
    'de': {
        '验证码': 'Sicherheitscode',
        '请输入答案': 'Antwort eingeben',
        '你的昵称': 'Dein Name',
        '写下你想说的话...': 'Schreibe, was du sagen möchtest...',
        '验证码错误': 'Sicherheitscode falsch',
    },
    'ja': {
        '验证码': '認証コード',
        '请输入答案': '答えを入力',
        '你的昵称': 'ニックネーム',
        '写下你想说的话...': '伝えたいことを書いてください...',
        '验证码错误': '認証コードが違います',
    },
    'es': {
        '验证码': 'Código de verificación',
        '请输入答案': 'Introduce la respuesta',
        '你的昵称': 'Tu apodo',
        '写下你想说的话...': 'Escribe lo que quieres decir...',
        '验证码错误': 'Código de verificación incorrecto',
    },
    'pt': {
        '验证码': 'Código de verificação',
        '请输入答案': 'Digite a resposta',
        '你的昵称': 'Seu apelido',
        '写下你想说的话...': 'Escreva o que você quer dizer...',
        '验证码错误': 'Código de verificação incorreto',
    },
    'fr': {
        '验证码': 'Code de vérification',
        '请输入答案': 'Entrez la réponse',
        '你的昵称': 'Votre pseudo',
        '写下你想说的话...': 'Écrivez ce que vous voulez dire...',
        '验证码错误': 'Code de vérification incorrect',
    },
}

for locale, mapping in EXTRA.items():
    po_path = BASE / locale / 'LC_MESSAGES' / 'django.po'
    po = polib.pofile(str(po_path))
    for entry in po:
        if entry.msgid in mapping and not entry.msgstr:
            entry.msgstr = mapping[entry.msgid]
    po.save()
    print(f'Updated {locale}')
