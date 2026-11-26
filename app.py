"""POST /triage: вызывается из n8n (Webhook/Telegram -> HTTP Request). Лог в SQLite."""
import json
import os
import sqlite3
import time

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

load_dotenv()
from triage import triage  # noqa: E402

app = FastAPI(title="Ticket Triage LLM")
DB = "tickets.db"


class Ticket(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


@app.post("/triage")
def triage_endpoint(t: Ticket, x_token: str = Header(default="")):
    if x_token != os.getenv("WEBHOOK_TOKEN", "__unset__"):
        raise HTTPException(status_code=401, detail="bad token")
    result = triage(t.text)
    with sqlite3.connect(DB) as c:  # в лог пишем уже результат, а не сырой текст
        c.execute("CREATE TABLE IF NOT EXISTS triage(ts REAL, result TEXT)")
        c.execute("INSERT INTO triage VALUES (?,?)", (time.time(), json.dumps(result, ensure_ascii=False)))
    return result
