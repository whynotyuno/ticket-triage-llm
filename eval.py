"""Оценка качества: сравнение ответов модели с ручной разметкой в data/tickets.json."""
import json

from dotenv import load_dotenv

load_dotenv()
from triage import triage  # noqa: E402

cases = json.load(open("data/tickets.json", encoding="utf-8"))
cat_ok = urg_ok = 0
for c in cases:
    r = triage(c["text"])
    a, b = r["category"] == c["category"], r["urgency"] == c["urgency"]
    cat_ok += a
    urg_ok += b
    mark = "OK  " if a and b else "FAIL"
    print(f"{mark} {c['text'][:55]!r:60} -> {r['category']}/{r['urgency']} (ожидалось {c['category']}/{c['urgency']})")
n = len(cases)
print(f"\nКатегория: {cat_ok}/{n}   Срочность: {urg_ok}/{n}")
