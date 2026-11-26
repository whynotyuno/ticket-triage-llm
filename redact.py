"""Маскирование персональных данных ДО отправки текста во внешний API."""
import re

_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    (re.compile(r"(?:\+7|8)[\s(-]*\d{3}[\s)-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}"), "[PHONE]"),
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[CARD]"),
]


def redact(text: str) -> str:
    for rx, repl in _PATTERNS:
        text = rx.sub(repl, text)
    return text
