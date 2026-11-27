"""Оценка качества: сравнение ответов модели с ручной разметкой в data/tickets.json.
Запуск: python eval.py            (все обращения)
        python eval.py --limit 10 (только первые 10, чтобы сэкономить)"""
import argparse
import json
from collections import defaultdict

from dotenv import load_dotenv

load_dotenv()
from triage import triage  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--limit", type=int, default=None)
args = ap.parse_args()

cases = json.load(open("data/tickets.json", encoding="utf-8"))[: args.limit]
by_tag = defaultdict(lambda: [0, 0])      # tag -> [верно, всего] по категории
by_cat = defaultdict(lambda: [0, 0])
cat_ok = urg_ok = both_ok = 0
fails = []

for c in cases:
    try:
        r = triage(c["text"])
    except Exception as e:            # одна ошибка API не должна ронять весь прогон
        print("ОШИБКА", repr(c["text"][:40]), e)
        r = {"category": "?", "urgency": "?"}
    a, b = r["category"] == c["category"], r["urgency"] == c["urgency"]
    cat_ok += a; urg_ok += b; both_ok += (a and b)
    for k, store in ((c["tag"], by_tag), (c["category"], by_cat)):
        store[k][0] += a; store[k][1] += 1
    if not (a and b):
        fails.append((c, r))

n = len(cases)
print(f"Категория: {cat_ok}/{n} ({cat_ok/n:.0%})   Срочность: {urg_ok}/{n} ({urg_ok/n:.0%})   Обе верно: {both_ok}/{n}")
print("\nТочность категории по классам:", {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_cat.items())})
print("Точность категории по типам обращений:", {k: f"{v[0]}/{v[1]}" for k, v in sorted(by_tag.items())})
print(f"\n--- Ошибки ({len(fails)}) ---")
for c, r in fails:
    print(f"* {c['text'][:70]!r}\n    модель: {r['category']}/{r['urgency']}   разметка: {c['category']}/{c['urgency']}   [{c['tag']}]")
