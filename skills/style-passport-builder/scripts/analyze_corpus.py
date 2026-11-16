#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор корпуса текстов автора.
Извлекает детерминированные метрики: синтаксис, ритмику, пунктуацию, эмодзи,
частотные связки и отбирает эталонные тексты для Паспорта стиля.
"""

import sys
import os
import re
import json
import unicodedata
from collections import Counter

def extract_text_from_telegram_json(data):
    """Извлекает тексты постов из экспорта Telegram (result.json)."""
    texts = []
    messages = data.get("messages", [])
    for msg in messages:
        if msg.get("type") != "message":
            continue
        raw_text = msg.get("text", "")
        clean_text = ""
        if isinstance(raw_text, str):
            clean_text = raw_text.strip()
        elif isinstance(raw_text, list):
            parts = []
            for part in raw_text:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict) and "text" in part:
                    parts.append(part["text"])
            clean_text = "".join(parts).strip()
        
        # Игнорируем совсем короткие служебные отбивки и опросы
        if len(clean_text) >= 50:
            texts.append(clean_text)
    return texts

def extract_texts_from_file_or_dir(target_path):
    """Считывает тексты из файла или папки."""
    texts = []
    if os.path.isfile(target_path):
        if target_path.endswith(".json"):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    texts = extract_text_from_telegram_json(data)
            except Exception as e:
                print(f"Ошибка чтения JSON: {e}", file=sys.stderr)
        else:
            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
                # Разделяем постеры по двойным переносам или спецразделителям
                blocks = re.split(r'\n{3,}|\n---+\n', content)
                for b in blocks:
                    clean = b.strip()
                    if len(clean) >= 40:
                        texts.append(clean)
    elif os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith((".txt", ".md", ".json")):
                    fp = os.path.join(root, file)
                    if file.endswith(".json"):
                        try:
                            with open(fp, "r", encoding="utf-8") as f:
                                texts.extend(extract_text_from_telegram_json(json.load(f)))
                        except:
                            pass
                    else:
                        try:
                            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                                c = f.read().strip()
                                blocks = re.split(r'\n{3,}|\n---+\n', c)
                                for b in blocks:
                                    clean = b.strip()
                                    if len(clean) >= 40:
                                        texts.append(clean)
                        except:
                            pass
    return texts

def analyze_corpus(texts):
    """Анализирует список текстов и рассчитывает метрики синтаксиса и пунктуации."""
    if not texts:
        return {"error": "Тексты для анализа не найдены"}

    total_posts = len(texts)
    post_lengths_chars = [len(t) for t in texts]
    
    words_all = []
    sentences_all = []
    paragraphs_all = []
    emojis_all = []

    # Регулярки
    sentence_splitter = re.compile(r'(?<=[.!?…])\s+(?=[А-ЯA-Z0-9«"A-Za-zА-Яа-я])')
    word_splitter = re.compile(r'[А-Яа-яA-Za-z0-9ёЁ\-]+')
    
    # Пунктуационные счетчики
    punct_counts = {
        "em_dash": 0,      # —
        "en_dash": 0,      # –
        "hyphen": 0,       # -
        "ellipsis": 0,     # ... или …
        "exclamation": 0,  # !
        "question": 0,     # ?
        "quotes_angle": 0, # « »
        "quotes_straight": 0, # "
        "parentheses": 0,  # ( )
        "colon": 0,        # :
        "semicolon": 0     # ;
    }

    for t in texts:
        # Абзацы
        paras = [p.strip() for p in t.split("\n") if p.strip()]
        paragraphs_all.extend(paras)

        # Пунктуация
        punct_counts["em_dash"] += t.count("—")
        punct_counts["en_dash"] += t.count("–")
        punct_counts["hyphen"] += len(re.findall(r'(?<=\s)-(?=\s)', t))
        punct_counts["ellipsis"] += len(re.findall(r'\.{3}|…', t))
        punct_counts["exclamation"] += t.count("!")
        punct_counts["question"] += t.count("?")
        punct_counts["quotes_angle"] += t.count("«") + t.count("»")
        punct_counts["quotes_straight"] += t.count('"')
        punct_counts["parentheses"] += t.count("(") + t.count(")")
        punct_counts["colon"] += t.count(":")
        punct_counts["semicolon"] += t.count(";")

        # Эмодзи (диапазоны реальных эмодзи без ASCII-символов и кавычек)
        for char in t:
            code = ord(char)
            if (0x1F600 <= code <= 0x1F64F or # Emoticons
                0x1F300 <= code <= 0x1F5FF or # Misc Symbols and Pictographs
                0x1F680 <= code <= 0x1F6FF or # Transport and Map
                0x1F900 <= code <= 0x1F9FF or # Supplemental Symbols and Pictographs
                0x1FA70 <= code <= 0x1FAFF or # Symbols and Pictographs Extended-A
                0x2600 <= code <= 0x26FF or   # Misc Symbols
                0x2700 <= code <= 0x27BF):    # Dingbats
                emojis_all.append(char)

        # Предложения
        s_list = sentence_splitter.split(t)
        for s in s_list:
            s_clean = s.strip()
            if s_clean:
                w_list = word_splitter.findall(s_clean)
                if w_list:
                    sentences_all.append(w_list)
                    words_all.extend(w_list)

    total_words = len(words_all)
    total_sentences = len(sentences_all)
    sentence_lengths = [len(s) for s in sentences_all] if sentences_all else [0]
    
    # Распределение предложений по длине
    short_sentences = sum(1 for sl in sentence_lengths if sl <= 7)
    medium_sentences = sum(1 for sl in sentence_lengths if 8 <= sl <= 16)
    long_sentences = sum(1 for sl in sentence_lengths if sl > 16)

    # N-граммы (биграммы и триграммы)
    lowercase_words = [w.lower() for w in words_all if len(w) > 2]
    bigrams = [f"{lowercase_words[i]} {lowercase_words[i+1]}" for i in range(len(lowercase_words)-1)]
    bigram_counts = Counter(bigrams).most_common(15)

    # Топ эмодзи
    emoji_counts = Counter(emojis_all).most_common(10)

    # Нормализация пунктуации на 1000 слов
    norm_factor = 1000.0 / max(total_words, 1)
    punct_per_1000 = {k: round(v * norm_factor, 2) for k, v in punct_counts.items()}

    # Отбор эталонных постов (3-5 постов около медианной длины с хорошей связностью)
    sorted_posts = sorted(texts, key=lambda x: len(x))
    median_len = sorted_posts[len(sorted_posts)//2] if sorted_posts else ""
    median_chars = len(median_len)
    
    # Близкие к медиане посты без технических ссылок
    candidate_samples = [
        p for p in texts 
        if 0.7 * median_chars <= len(p) <= 1.4 * median_chars and not p.startswith("http")
    ]
    sample_posts = candidate_samples[:4] if len(candidate_samples) >= 4 else texts[:4]

    report = {
        "corpus_summary": {
            "posts_count": total_posts,
            "total_words": total_words,
            "total_characters": sum(post_lengths_chars),
            "avg_chars_per_post": round(sum(post_lengths_chars) / total_posts, 1),
            "min_chars_post": min(post_lengths_chars),
            "max_chars_post": max(post_lengths_chars)
        },
        "syntax_biometrics": {
            "total_sentences": total_sentences,
            "avg_words_per_sentence": round(sum(sentence_lengths) / max(total_sentences, 1), 1),
            "sentence_distribution_pct": {
                "short_under_8_words": round(short_sentences / max(total_sentences, 1) * 100, 1),
                "medium_8_to_16_words": round(medium_sentences / max(total_sentences, 1) * 100, 1),
                "long_over_16_words": round(long_sentences / max(total_sentences, 1) * 100, 1)
            }
        },
        "paragraph_structure": {
            "total_paragraphs": len(paragraphs_all),
            "avg_sentences_per_paragraph": round(total_sentences / max(len(paragraphs_all), 1), 1),
            "avg_chars_per_paragraph": round(sum(len(p) for p in paragraphs_all) / max(len(paragraphs_all), 1), 1)
        },
        "punctuation_per_1000_words": punct_per_1000,
        "emoji_profile": {
            "total_emojis": len(emojis_all),
            "emojis_per_1000_chars": round(len(emojis_all) / max(sum(post_lengths_chars), 1) * 1000, 2),
            "top_emojis": emoji_counts
        },
        "frequent_phrases": [b[0] for b in bigram_counts],
        "representative_samples": sample_posts
    }
    return report

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
        
    if len(sys.argv) < 2:
        print("Использование: python analyze_corpus.py <путь_к_файлу_или_папке> [выходной_файл.json]")
        sys.exit(1)
        
    target_path = sys.argv[1]
    texts = extract_texts_from_file_or_dir(target_path)
    
    if not texts:
        print(f"Ошибка: не удалось извлечь тексты из {target_path}", file=sys.stderr)
        sys.exit(1)
        
    report = analyze_corpus(texts)
    output_json = json.dumps(report, ensure_ascii=False, indent=2)
    
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"Анализ завершен. Результаты сохранены в {out_path}")
    else:
        print(output_json)

if __name__ == "__main__":
    main()
