# Ticket Triage LLM

Сервис, который разбирает обращения клиентов интернет-магазина: определяет **категорию** и **срочность**,
вытаскивает **номер заказа**, пишет **черновик ответа** и решает, нужен ли человек. Подключается к n8n.

Данные в проекте вымышленные (`data/tickets.json`), персональных данных нет.

## Как устроено
Webhook / Telegram (n8n) -> `POST /triage` -> маскирование ПДн -> LLM (structured output) -> проверка ответа -> n8n (таблица / уведомление).

| Файл | Назначение |
|---|---|
| `triage.py` | вызов Anthropic API, форсированный structured output (`tool_choice`), валидация ответа, fallback на человека |
| `redact.py` | маскирование email, телефонов и номеров карт перед отправкой в API |
| `app.py` | FastAPI `POST /triage`, токен в заголовке, лог результатов в SQLite |
| `eval.py` | оценка точности на 42 размеченных обращениях (включая prompt injection, английский, короткие и неоднозначные случаи; отчёт по типам и список ошибок) |
| `tests/` | офлайн-тесты (API имитируется) |

## Безопасность
- Ключ в переменных окружения, `.env` в `.gitignore`.
- Email, телефоны и карты маскируются до отправки; текст обрезается до 2000 символов.
- Текст обращения в промпте помечен как данные; есть тест-кейс с prompt injection.
- Ответ модели проверяется кодом: неизвестная категория -> `needs_human=true`.
- Сырой текст обращений в лог не пишется.

## Запуск (Windows PowerShell)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # впишите ключ
python tests\test_triage.py # офлайн-тесты
python eval.py              # реальные вызовы API
uvicorn app:app --reload    # http://127.0.0.1:8000/docs
```

## Сценарий в n8n
1. **Webhook** (или Telegram Trigger): принимает текст обращения.
2. **HTTP Request**: POST `http://localhost:8000/triage`, заголовок `X-Token: <WEBHOOK_TOKEN>`, тело `{"text": "{{ $json.text }}"}`.
   (Если n8n в Docker, вместо localhost используйте `host.docker.internal`.)
3. **IF**: `needs_human` = true ИЛИ `urgency` = high.
4. Ветка «да»: уведомление в Telegram дежурному. Ветка «нет»: строка в Google Sheets с черновиком ответа.

## Результаты
Категория: 40/42 (95%)   Срочность: 35/42 (83%)   Обе верно: 33/42

## Идеи развития
PostgreSQL вместо SQLite, Redis-кэш для одинаковых обращений, RAG по базе знаний для черновиков ответа.
