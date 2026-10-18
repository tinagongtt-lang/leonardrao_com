import os
import pathlib
import time

os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
os.environ.setdefault('USE_TF', '0')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

import polib
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

BASE = pathlib.Path(__file__).parent

LOCALE_TO_NLLB = {
    'zh_Hant': 'zho_Hant',
    'en_US': 'eng_Latn',
    'en_GB': 'eng_Latn',
    'en_AU': 'eng_Latn',
    'de': 'deu_Latn',
    'ja': 'jpn_Jpan',
    'es': 'spa_Latn',
    'pt': 'por_Latn',
    'fr': 'fra_Latn',
    'it': 'ita_Latn',
    'ru': 'rus_Cyrl',
    'ko': 'kor_Hang',
    'ar': 'ara_Arab',
    'nl': 'nld_Latn',
    'pl': 'pol_Latn',
    'tr': 'tur_Latn',
    'vi': 'vie_Latn',
    'th': 'tha_Thai',
    'sv': 'swe_Latn',
}

SRC_LANG = 'zho_Hans'
MODEL = 'facebook/nllb-200-distilled-600M'
BATCH_SIZE = 8


def load_model():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'Loading {MODEL} on {device}...')
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL,
        torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
    ).to(device)
    model.eval()
    return tokenizer, model, device


def translate_batch(tokenizer, model, device, texts, tgt_lang):
    tokenizer.src_lang = SRC_LANG
    inputs = tokenizer(
        texts,
        return_tensors='pt',
        padding=True,
        truncation=True,
        max_length=128,
    ).to(device)
    forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_lang)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_length=128,
            num_beams=2,
            early_stopping=True,
        )
    return tokenizer.batch_decode(outputs, skip_special_tokens=True)


def main(overwrite: bool = False):
    tokenizer, model, device = load_model()

    for locale, tgt_lang in LOCALE_TO_NLLB.items():
        po_path = BASE / locale / 'LC_MESSAGES' / 'django.po'
        if not po_path.exists():
            print(f'Skipping {locale}: {po_path} not found')
            continue
        po = polib.pofile(str(po_path))
        entries = [e for e in po if overwrite or not e.msgstr]
        if not entries:
            print(f'Skipping {locale}: nothing to translate')
            continue
        print(f'Translating {locale} ({len(entries)} entries) -> {tgt_lang}')

        for i in range(0, len(entries), BATCH_SIZE):
            batch = entries[i:i + BATCH_SIZE]
            texts = [e.msgid for e in batch]
            try:
                results = translate_batch(tokenizer, model, device, texts, tgt_lang)
            except Exception as exc:
                print(f'Error translating batch for {locale}: {exc}')
                continue
            for entry, result in zip(batch, results):
                entry.msgstr = result
                print(f'  [{locale}] {entry.msgid!r} -> {result!r}')

        po.save()
        print(f'Saved {locale}')


if __name__ == '__main__':
    import sys
    overwrite = '--overwrite' in sys.argv
    main(overwrite=overwrite)
