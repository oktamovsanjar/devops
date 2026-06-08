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
import profile  # noqa: E402  (o'rganilgan mavzular — learner model)
from generate import load_key  # noqa: E402

API = "https://api.telegram.org/bot{token}/{method}"
HELP = (
    "🤖 <b>DevOps Quiz Bot</b>\n\n"
    "▸ /quiz — bugungi mavzu quizini boshlash\n"
    "   Javob ber → keyingisi avtomatik keladi 🔁\n"
    "   To'g'ri → daraja 📈  ·  xato → 📉\n\n"
    "▸ /topic &lt;mavzu&gt; — boshqa mavzuni tanlash\n"
    "▸ /daily — bugungi mavzuga qaytish\n"
    "▸ /stop — to'xtatish  ·  /reset — daraja 1 ga\n"
    "▸ /help — yordam"
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


TOPIC_EMOJI = {
    "linux": "🐧", "bash": "💻", "git": "🌿", "networking": "🌐", "docker": "🐳",
    "cicd": "🔁", "kubernetes": "☸️", "terraform": "🏗️", "ansible": "📜",
    "aws": "☁️", "monitoring": "📈", "python": "🐍", "english": "🔤",
}


def _pool_topics(con):
    """DEFAULT = bugungi kun mavzu(lar)i. /topic bilan o'zgartirilgan bo'lsa — o'sha."""
    learned = set(profile.learned_topics(con))
    override = db.get_meta(con, "tg_topic")
    if override and override in learned:
        return {override}
    day = int(db.get_meta(con, "current_day", "1"))
    wk = {t for t in profile.WEEK_TOPICS.get(profile.current_week(day), []) if t in learned}
    return wk or learned                      # zaxira: o'rganilgan hammasi


def _pool_questions(con):
    topics = _pool_topics(con)
    day = int(db.get_meta(con, "current_day", "1"))
    taught = con.execute("SELECT id, topic, difficulty FROM questions "
                         "WHERE day IS NOT NULL AND day<=?", (day,)).fetchall()
    pool = [r for r in taught if r["topic"] in topics]      # faqat O'RGATILGAN kun savollari
    if pool:
        return pool
    rows = con.execute("SELECT id, topic, difficulty FROM questions").fetchall()
    return [r for r in rows if r["topic"] in topics]        # zaxira (day-savollar hali yo'q bo'lsa)


def next_adaptive_question(con):
    rows = _pool_questions(con)
    if not rows:
        return None
    avail = sorted({r["difficulty"] for r in rows})
    level, _ = get_level(con)
    if level not in avail:
        level = min(avail, key=lambda x: abs(x - level))
    target = level
    if level > avail[0] and random.random() < REVIEW_PROB:        # orada past daraja takrori
        target = max(avail[0], level - random.choice([1, 2]))
    recent = _recent_qids(con, n=25)                              # yaqinda yuborilganlarni chetla
    weak = set(quizplan.weak_topics(con))
    fresh = [r for r in rows if r["id"] not in recent] or rows    # takror FAQAT hammasi ishlatilganda
    nearest = min((r["difficulty"] for r in fresh),               # target'ga eng yaqin, fresh daraja
                  key=lambda d: (abs(d - target), d))
    band = [r for r in fresh if r["difficulty"] == nearest]
    pool = []
    for r in band:
        pool.append(r["id"])
        if r["topic"] in weak:
            pool.append(r["id"])                                  # zaif mavzu 2x og'irlik
    qid = random.choice(pool)
    return con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()


def level_msg(change, level):
    if change == "up":
        return f"📈 <b>Zo'r! Daraja OSHDI → {level}</b> 🔥\nEndi qiyinroq savollar keladi."
    return f"📉 <b>Daraja tushdi → {level}</b>\nShu darajani mustahkamlaymiz (takror)."


def start_banner(con):
    day = int(db.get_meta(con, "current_day", "1"))
    topics = sorted(_pool_topics(con))
    level, _ = get_level(con)
    r = con.execute("SELECT COUNT(*) n, SUM(correct) ok FROM attempts "
                    "WHERE date(ts)=date('now')").fetchone()
    n, ok = r["n"] or 0, r["ok"] or 0
    tline = ", ".join(f"{TOPIC_EMOJI.get(t, '•')} {t.capitalize()}" for t in topics) or "umumiy"
    return ("🎯 <b>Bugungi quiz boshlandi</b>\n"
            f"📅 Day {day}/56  ·  mavzu: {tline}\n"
            f"📊 Daraja: <b>{level}</b>  ·  bugun: {ok}/{n} to'g'ri\n\n"
            "Javob ber — keyingisi avtomatik keladi.  /help")


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
    emoji = TOPIC_EMOJI.get(q["topic"], "•")
    stars = "⭐" * int(q["difficulty"])
    header = f"{emoji} {q['topic'].capitalize()} · {stars}"
    res = api(token, "sendPoll", {
        "chat_id": chat_id,
        "question": f"{header}\n\n{q['question']}"[:300],
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
        if text in ("/start", "/quiz", "/next", "/daily"):
            if text == "/daily":
                db.set_meta(con, "tg_topic", "")          # override'ni tozalab, kunlikка qaytar
            db.set_meta(con, "tg_active", "1")
            send_msg(token, chat_id, start_banner(con))
            send_quiz(token, chat_id, con, key)
        elif text.startswith("/topic"):
            learned = sorted(profile.learned_topics(con))
            parts = text.split()
            if len(parts) >= 2 and parts[1] in learned:
                db.set_meta(con, "tg_topic", parts[1])
                send_msg(token, chat_id, f"✅ Mavzu tanlandi: <b>{parts[1]}</b>. "
                                         "Kunlikка qaytish: /daily")
                send_quiz(token, chat_id, con, key)
            else:
                tl = ", ".join(learned) or "—"
                send_msg(token, chat_id, f"📚 O'rganilgan mavzular: {tl}\n"
                                         f"Misol:  /topic {learned[-1] if learned else 'linux'}")
        elif text == "/stop":
            db.set_meta(con, "tg_active", "0")
            send_msg(token, chat_id, "⏸️ Quiz to'xtatildi. Qayta boshlash: /quiz")
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
