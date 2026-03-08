import asyncio
import re
import time
from pathlib import Path
from googletrans import Translator, LANGUAGES


def CodeLang(lang: str) -> str:
    """
    Якщо передано код мови -> повертає назву мови.
    Якщо передано назву мови -> повертає код мови.
    Якщо мову не знайдено -> повертає повідомлення про помилку.
    """
    if not isinstance(lang, str) or not lang.strip():
        return "Language not found"

    lang = lang.strip().lower()

    if lang in LANGUAGES:
        return LANGUAGES[lang].title()

    for code, name in LANGUAGES.items():
        if name.lower() == lang:
            return code

    return "Language not found"


def normalize_lang(lang: str) -> str | None:
    """
    Повертає код мови:
    - якщо передали код -> повертає його
    - якщо передали назву -> знаходить відповідний код
    """
    if not isinstance(lang, str) or not lang.strip():
        return None

    lang = lang.strip().lower()

    if lang in LANGUAGES:
        return lang

    for code, name in LANGUAGES.items():
        if name.lower() == lang:
            return code

    return None


async def TransLate(text: str, lang: str) -> str:
    """
    Переклад тексту на вказану мову.
    text - текст для перекладу
    lang - назва мови або її код
    """
    if not isinstance(text, str) or not text.strip():
        return "Translation error: empty text"

    dest_code = normalize_lang(lang)
    if not dest_code:
        return "Translation error: language not found"

    try:
        async with Translator() as translator:
            result = await translator.translate(text, dest=dest_code)
            return result.text
    except Exception as e:
        return f"Translation error: {e}"


async def LangDetect(txt: str) -> tuple[str, float]:
    """
    Повертає код мови тексту та confidence.
    """
    if not isinstance(txt, str) or not txt.strip():
        return "unknown", 0.0

    try:
        async with Translator() as translator:
            result = await translator.detect(txt)
            confidence = result.confidence if result.confidence is not None else 0.0
            return result.lang, confidence
    except Exception:
        return "unknown", 0.0


def split_sentences(text: str) -> list[str]:
    """
    Розбиває текст на окремі речення.
    """
    text = re.sub(r"\s+", " ", text.strip())
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def read_text(file_name: str) -> tuple[str, str]:
    """
    Читає текст із файлу.
    Повертає ім'я файлу та його вміст.
    """
    path = Path(file_name)

    if not path.exists():
        raise FileNotFoundError(f"File '{file_name}' not found")

    text = path.read_text(encoding="utf-8")
    return path.name, text


async def sync_translate(sentences: list[str], lang: str):
    """
    Синхронний режим:
    послідовно перекладає кожне речення.
    """
    start = time.perf_counter()

    translated = []
    for sentence in sentences:
        result = await TransLate(sentence, lang)
        translated.append(result)

    end = time.perf_counter()
    return translated, end - start


async def async_translate(sentences: list[str], lang: str):
    """
    Асинхронний режим:
    одночасно перекладає всі речення.
    """
    start = time.perf_counter()

    tasks = [TransLate(sentence, lang) for sentence in sentences]
    translated = await asyncio.gather(*tasks)

    end = time.perf_counter()
    return translated, end - start


async def main():
    file_name = "steve_jobs.txt"
    target_lang = "it"   # Italian

    try:
        file_title, text = read_text(file_name)
        print(f"File name: {file_title}")
    except Exception as e:
        print(f"File reading error: {e}")
        return

    sentences = split_sentences(text)

    print(f"Characters: {len(text)}")
    print(f"Sentences: {len(sentences)}")

    original_lang_code, confidence = await LangDetect(text)

    print(f"Original language: {CodeLang(original_lang_code)}")
    print(f"Language code: {original_lang_code}")
    print(f"Confidence: {confidence}")

    print("\nOriginal text:\n")
    print(text)

    target_code = normalize_lang(target_lang)
    if not target_code:
        print("\nTarget language error: language not found")
        return

    print(f"\nTarget language: {CodeLang(target_code)}")
    print(f"Target language code: {target_code}")

    # Синхронний переклад
    sync_tr, sync_time = await sync_translate(sentences, target_lang)

    print("\n--- SYNCHRONOUS TRANSLATION ---")
    print(" ".join(sync_tr))
    print(f"Time: {sync_time:.4f} sec")

    # Асинхронний переклад
    async_tr, async_time = await async_translate(sentences, target_lang)

    print("\n--- ASYNCHRONOUS TRANSLATION ---")
    print(" ".join(async_tr))
    print(f"Time: {async_time:.4f} sec")


if __name__ == "__main__":
    asyncio.run(main())