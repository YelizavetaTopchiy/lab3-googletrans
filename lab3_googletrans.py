import asyncio
import re
import time
from pathlib import Path
from googletrans import Translator, LANGUAGES


def CodeLang(lang: str):
    lang = lang.lower()

    if lang in LANGUAGES:
        return LANGUAGES[lang]

    for code, name in LANGUAGES.items():
        if name.lower() == lang:
            return code

    return "Language not found"


async def TransLate(text: str, lang: str):
    try:
        async with Translator() as translator:
            result = await translator.translate(text, dest=lang)
            return result.text
    except Exception as e:
        return f"Translation error: {e}"


async def LangDetect(txt: str):
    try:
        async with Translator() as translator:
            result = await translator.detect(txt)
            return result.lang, result.confidence
    except:
        return "unknown", 0


def split_sentences(text):
    sentences = re.split(r'[.!?]', text)
    return [s.strip() for s in sentences if s.strip()]


def read_text(file_name):
    path = Path(file_name)

    if not path.exists():
        print("File not found")
        return ""

    with open(file_name, encoding="utf-8") as f:
        return f.read()


async def sync_translate(sentences, lang):
    start = time.time()

    translated = []

    for s in sentences:
        tr = await TransLate(s, lang)
        translated.append(tr)

    end = time.time()

    return translated, end - start


async def async_translate(sentences, lang):
    start = time.time()

    tasks = [TransLate(s, lang) for s in sentences]

    translated = await asyncio.gather(*tasks)

    end = time.time()

    return translated, end - start


async def main():

    file_name = "steve_jobs.txt"
    target_lang = "en"

    text = read_text(file_name)

    if not text:
        return

    sentences = split_sentences(text)

    print("File name:", file_name)
    print("Characters:", len(text))
    print("Sentences:", len(sentences))

    lang, conf = await LangDetect(text)

    print("Original language:", CodeLang(lang))
    print("Language code:", lang)
    print("Confidence:", conf)

    print("\nOriginal text:\n")
    print(text)

    print("\nTarget language:", CodeLang(target_lang))
    print("Target language code:", target_lang)

    sync_tr, sync_time = await sync_translate(sentences, target_lang)

    print("\n--- SYNCHRONOUS TRANSLATION ---")
    print(" ".join(sync_tr))
    print("Time:", sync_time)

    async_tr, async_time = await async_translate(sentences, target_lang)

    print("\n--- ASYNCHRONOUS TRANSLATION ---")
    print(" ".join(async_tr))
    print("Time:", async_time)


if __name__ == "__main__":
    asyncio.run(main())