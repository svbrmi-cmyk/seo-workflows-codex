#!/usr/bin/env python3
"""Текст из .docx по абзацам, без сторонних библиотек.

Использование:
    python3 docx_text.py FILE.docx [FILE2.docx]

С двумя файлами сравнивает их текст и сообщает, совпадают ли они.
"""
import re
import sys
import zipfile


def paragraphs(path):
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
        s = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip()
        if s:
            out.append(s)
    return out


if __name__ == "__main__":
    if len(sys.argv) == 3:
        a, b = paragraphs(sys.argv[1]), paragraphs(sys.argv[2])
        print("SAME" if a == b else "DIFFERENT")
    else:
        print("\n".join(paragraphs(sys.argv[1])))
