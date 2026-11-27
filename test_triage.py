import os
import sys
from types import SimpleNamespace as NS

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from redact import redact
import triage as tr


def test_redact():
    s = redact("Пишите на ivan@mail.ru или +7 909 902-47-40, карта 4276 1234 5678 9012")
    assert "ivan@mail.ru" not in s and "902-47-40" not in s and "4276" not in s
    assert "[EMAIL]" in s and "[PHONE]" in s and "[CARD]" in s


class Fake:
    def __init__(self, tool_input):
        self.seen = None
        self.tool_input = tool_input
        self.messages = NS(create=self.create)

    def create(self, **kw):
        self.seen = kw
        blk = NS(type="tool_use", name="submit_triage", input=self.tool_input)
        return NS(content=[blk])


def test_ok_and_masking():
    f = Fake({"category": "payment", "urgency": "high", "summary": "s", "needs_human": False, "draft_reply": "r"})
    out = tr.triage("Деньги списались дважды, мой email a@b.ru", client=f)
    assert out["category"] == "payment" and out["urgency"] == "high"
    assert "a@b.ru" not in f.seen["messages"][0]["content"]   # персональные данные не ушли в API
    assert f.seen["tool_choice"]["name"] == "submit_triage"


def test_bad_model_output_goes_to_human():
    f = Fake({"category": "HACKED", "urgency": "high", "summary": "s", "needs_human": False, "draft_reply": "r"})
    assert tr.triage("текст", client=f)["needs_human"] is True


def test_empty_rejected():
    try:
        tr.triage("   ", client=Fake({}))
    except ValueError:
        return
    raise AssertionError("ожидали ValueError")


def test_dataset_valid():
    import json
    data = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tickets.json"), encoding="utf-8"))
    assert 30 <= len(data) <= 50
    for d in data:
        assert d["category"] in tr.CATEGORIES and d["urgency"] in tr.URGENCY and d["text"].strip()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("OK", name)
