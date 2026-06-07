#!/usr/bin/env python3
"""
DevOps Bootcamp — Telegram kunlik quiz yuboruvchi.
Telegram'ning native "quiz poll" funksiyasidan foydalanadi
(to'g'ri javob belgilanadi, javob bergach tushuntirish chiqadi).

Foydalanish:
  python3 quiz.py              # istalgan mavzudan tasodifiy savol
  python3 quiz.py linux        # faqat 'linux' bankidan
  python3 quiz.py --list       # mavjud mavzular
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notify import load_creds, api_call  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "quizbank")


def load_questions(topic=None):
    qs = []
    if topic:
        files = [os.path.join(BANK, f"{topic}.json")]
    else:
        files = [os.path.join(BANK, f) for f in sorted(os.listdir(BANK)) if f.endswith(".json")]
    for fp in files:
        if os.path.exists(fp):
            with open(fp, encoding="utf-8") as f:
                qs.extend(json.load(f))
    return qs


def send_quiz(token, chat_id, q):
    opts = q["options"]
    order = list(range(len(opts)))
    random.shuffle(order)                  # variantlarni aralashtiramiz
    display = [opts[i] for i in order]
    correct = order.index(q["correct"])
    params = {
        "chat_id": chat_id,
        "question": q["q"][:300],
        "options": json.dumps([o[:100] for o in display], ensure_ascii=False),
        "type": "quiz",
        "correct_option_id": correct,
        "is_anonymous": "false",
    }
    if q.get("explanation"):
        params["explanation"] = q["explanation"][:200]
    res = api_call(token, "sendPoll", params)
    if not res.get("ok"):
        print("❌ Xato:", res, file=sys.stderr)
        sys.exit(1)
    print("✅ Quiz yuborildi:", q["q"][:60])


def main():
    args = sys.argv[1:]
    if args and args[0] == "--list":
        topics = [f[:-5] for f in sorted(os.listdir(BANK)) if f.endswith(".json")]
        print("Mavzular:", ", ".join(topics) or "(bo'sh)")
        return

    topic = args[0] if (args and not args[0].startswith("-")) else None
    token, chat_id = load_creds()
    if not token or not chat_id:
        print("❌ token yoki chat_id yo'q (config.json).", file=sys.stderr)
        sys.exit(2)

    qs = load_questions(topic)
    if not qs:
        print(f"❌ Savol topilmadi (mavzu: {topic}).", file=sys.stderr)
        sys.exit(1)

    send_quiz(token, chat_id, random.choice(qs))


if __name__ == "__main__":
    main()
