#!/usr/bin/env python3
"""
DevOps Bootcamp — Telegram quiz dvigateli (doimiy bot).

Ishlash tartibi:
  - Telegram'da /start yoki /quiz yozasan -> bot AI tuzgan rejadan 1-quizni yuboradi
  - Sen javob berasan -> javobing SRS/profilga yoziladi -> KEYINGI quiz darhol keladi
  - /stop -> oqimni to'xtatadi ; /plan -> bugungi rejani qayta tuzadi ; /help

systemd servis sifatida ishlaydi (server o'chmaydi). Long-polling, webhook emas.
"""
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.abspath(os.path.join(HERE, "..", "..", "engine"))
sys.path.insert(0, HERE)       # notify.py uchun
sys.path.insert(0, ENGINE)     # db, srs, quizplan, generate uchun

from notify import load_creds  # noqa: E402
import db  # noqa: E402
import srs  # noqa: E402
import quizplan  # noqa: E402
from generate import load_key  # noqa: E402

API = "https://api.telegram.org/bot{token}/{method}"
HELP = (
    "🤖 <b>DevOps Quiz Bot (adaptiv)</b>\n\n"
    "/quiz yoki /start — quiz oqimini boshlash\n"
    "Javob ber → keyingisi keladi 🔁\n"
    "To'g'ri qilsang daraja 📈 oshadi, xato qilsang 📉 tushadi.\n\n"
    "/stop — to'xtatish\n"
    "/reset — darajani 1 ga qaytarish\n"
    "/help — yordam"
)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def api(token, method, params, timeout=20):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(API.format(token=token, method=method), data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def send_msg(token, chat_id, text):
    try:
        api(token, "sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
    except Exception as e:
        log(f"send_msg err: {e}")


# ───────── Adaptiv qiyinlik (terminal bilan bir xil mantiq) ─────────
PROMOTE = 2
DEMOTE = 2
REVIEW_PROB = 0.25


def available_levels(con):
    return sorted(r[0] for r in con.execute("SELECT DISTINCT difficulty FROM questions"))


def get_level(con):
    levels = available_levels(con)
    lv = db.get_meta(con, "tg_level")
    if lv is None:
        lv = levels[0] if levels else 1
        db.set_meta(con, "tg_level", lv)
    return int(lv), levels


def apply_result(con, correct):
    """Javobga qarab darajani yangilaydi. (yangi_daraja, 'up'|'down'|None)."""
    level, levels = get_level(con)
    cs = int(db.get_meta(con, "tg_correct", "0") or 0)
    ws = int(db.get_meta(con, "tg_wrong", "0") or 0)
    idx = levels.index(level) if level in levels else 0
    change = None
    if correct:
        cs += 1; ws = 0
        if cs >= PROMOTE and idx < len(levels) - 1:
            level = levels[idx + 1]; cs = 0; change = "up"
    else:
        ws += 1; cs = 0
        if ws >= DEMOTE and idx > 0:
            level = levels[idx - 1]; ws = 0; change = "down"
    db.set_meta(con, "tg_level", level)
    db.set_meta(con, "tg_correct", cs)
    db.set_meta(con, "tg_wrong", ws)
    return level, change


def _recent_qids(con, n=12):
    return {r["question_id"] for r in
            con.execute("SELECT question_id FROM sent_polls ORDER BY ts DESC LIMIT ?", (n,))}


def pick_qid_at_level(con, level):
    rows = con.execute("SELECT id, topic FROM questions WHERE difficulty=?", (level,)).fetchall()
    if not rows:
        return None
    weak = set(quizplan.weak_topics(con))
    recent = _recent_qids(con)
    cands = [r for r in rows if r["id"] not in recent] or rows
    pool = []
    for r in cands:
        pool.append(r["id"])
        if r["topic"] in weak:
            pool.append(r["id"])          # zaif mavzu 2x og'irlik
    return random.choice(pool)


def next_adaptive_question(con):
    level, levels = get_level(con)
    if not levels:
        return None
    if level not in levels:
        level = min(levels, key=lambda x: abs(x - level))
    target = level
    if level > levels[0] and random.random() < REVIEW_PROB:     # orada past daraja takrori
        target = min(levels, key=lambda x: (abs(x - (level - random.choice([1, 2]))), x))
    qid = pick_qid_at_level(con, target)
    if qid is None:                                             # eng yaqin mavjud daraja
        for d in sorted(levels, key=lambda x: abs(x - target)):
            qid = pick_qid_at_level(con, d)
            if qid:
                break
    if qid is None:
        return None
    return con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()


def level_msg(change, level):
    if change == "up":
        return f"📈 <b>Zo'r! Daraja OSHDI → {level}</b> 🔥\nEndi qiyinroq savollar keladi."
    return f"📉 <b>Daraja tushdi → {level}</b>\nShu darajani mustahkamlaymiz (takror)."


def send_quiz(token, chat_id, con, key):
    q = next_adaptive_question(con)
    if not q:
        send_msg(token, chat_id, "⚠️ Bankda savol yo'q.")
        return False
    opts = json.loads(q["options"])
    order = list(range(len(opts)))
    random.shuffle(order)
    display = [opts[i] for i in order]
    correct = order.index(q["correct"])
    res = api(token, "sendPoll", {
        "chat_id": chat_id,
        "question": f"[{q['topic']} · d{q['difficulty']}] {q['question']}"[:300],
        "options": json.dumps([o[:100] for o in display], ensure_ascii=False),
        "type": "quiz",
        "correct_option_id": correct,
        "is_anonymous": "false",
        "explanation": (q["explanation"] or "")[:200],
    })
    if not res.get("ok"):
        log(f"sendPoll fail: {res}")
        return False
    poll_id = res["result"]["poll"]["id"]
    con.execute("INSERT OR REPLACE INTO sent_polls(poll_id, question_id, correct_pos) VALUES(?,?,?)",
                (poll_id, q["id"], correct))
    con.commit()
    return True


def handle_answer(con, poll_id, option_ids):
    """Javobni yozadi. correct (bool) yoki None (poll topilmasa) qaytaradi."""
    row = con.execute("SELECT * FROM sent_polls WHERE poll_id=?", (poll_id,)).fetchone()
    if not row:
        return None
    chosen = option_ids[0] if option_ids else -1
    correct = (chosen == row["correct_pos"])
    srs.record_answer(con, row["question_id"], correct, chosen)
    log(f"answer poll={poll_id} q={row['question_id']} correct={correct}")
    return correct


def process(con, token, chat_id, key, u):
    if "poll_answer" in u:
        pa = u["poll_answer"]
        correct = handle_answer(con, pa["poll_id"], pa.get("option_ids", []))
        if db.get_meta(con, "tg_active", "1") == "1":
            if correct is not None:
                level, change = apply_result(con, correct)
                if change:                       # daraja o'zgardi -> Telegram xabar
                    send_msg(token, chat_id, level_msg(change, level))
            time.sleep(1)                        # foydalanuvchi Telegram natijani ko'rsin
            send_quiz(token, chat_id, con, key)
    elif "message" in u:
        m = u["message"]
        if str(m.get("chat", {}).get("id")) != str(chat_id):
            return
        text = (m.get("text") or "").strip().lower()
        if text in ("/start", "/quiz", "/next"):
            db.set_meta(con, "tg_active", "1")
            level, _ = get_level(con)
            send_msg(token, chat_id,
                     f"🎯 Quiz boshlandi! Joriy daraja: <b>{level}</b>. "
                     "Javob ber — daraja shunga qarab o'zgaradi.")
            send_quiz(token, chat_id, con, key)
        elif text == "/stop":
            db.set_meta(con, "tg_active", "0")
            send_msg(token, chat_id, "⏸️ Quiz oqimi to'xtatildi. Qayta boshlash: /quiz")
        elif text == "/reset":
            lv = available_levels(con)
            db.set_meta(con, "tg_level", lv[0] if lv else 1)
            db.set_meta(con, "tg_correct", 0)
            db.set_meta(con, "tg_wrong", 0)
            send_msg(token, chat_id, "🔄 Daraja boshiga qaytarildi. /quiz bilan boshla.")
        else:
            send_msg(token, chat_id, HELP)


def main():
    token, chat_id = load_creds()
    if not token or not chat_id:
        log("token/chat_id yo'q — chiqdim")
        sys.exit(2)
    key = load_key()
    con = db.connect()
    db.init()
    db.ensure_state(con)
    offset = int(db.get_meta(con, "tg_offset", "0") or 0)
    if offset == 0:                       # birinchi ishga tushish: eski xabarlarni o'tkazib yubor
        try:
            ups = api(token, "getUpdates", {"timeout": 0}, timeout=15).get("result", [])
            if ups:
                offset = ups[-1]["update_id"] + 1
                db.set_meta(con, "tg_offset", offset)
                log(f"drained {len(ups)} eski update, offset={offset}")
        except Exception as e:
            log(f"drain err: {e}")
    log(f"quizbot started (offset={offset}, chat={chat_id})")
    while True:
        try:
            res = api(token, "getUpdates", {
                "offset": offset, "timeout": 30,
                "allowed_updates": json.dumps(["poll_answer", "message"]),
            }, timeout=40)
            updates = res.get("result", [])
        except Exception as e:
            log(f"getUpdates err: {e}")
            time.sleep(5)
            continue
        for u in updates:
            offset = u["update_id"] + 1
            db.set_meta(con, "tg_offset", offset)
            try:
                process(con, token, chat_id, key, u)
            except Exception as e:
                log(f"process err: {e}")


if __name__ == "__main__":
    main()
