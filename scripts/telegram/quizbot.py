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
import re
import sys
import threading
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
    "▸ ⚡ /blitz — 10 savollik sprint (ballli natija)\n"
    "▸ /progress — kun, streak, bugungi natija, o'rganilgan mavzular\n"
    "▸ 🏅 /badges — ochilgan nishonlar\n"
    "▸ /today — bugungi kun mavzusi\n"
    "▸ /topic &lt;mavzu&gt; — boshqa mavzuni tanlash\n"
    "▸ /daily — bugungi mavzuga qaytish\n"
    "▸ 🔔 /reminder — eslatmalar (on/off yoki vaqt)\n"
    "▸ /stop — to'xtatish  ·  /reset — daraja 1 ga\n"
    "▸ /help — yordam\n\n"
    "<b>Murojaatlar (admin):</b>\n"
    "▸ /reply &lt;id&gt; &lt;matn&gt; — foydalanuvchiga javob\n"
    "   (yoki forward'ga reply qilib yoz)\n"
    "▸ /users — murojaatchilar ro'yxati\n"
    "▸ /broadcast &lt;matn&gt; — hammaga xabar"
)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def api(token, method, params, timeout=20):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(API.format(token=token, method=method), data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def send_msg(token, chat_id, text, markup=None):
    params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if markup:
        params["reply_markup"] = markup
    try:
        api(token, "sendMessage", params)
    except Exception as e:
        log(f"send_msg err: {e}")


# ───────── Inline tugmalar (UI) ─────────
def kb(rows):
    return json.dumps({"inline_keyboard":
                       [[{"text": t, "callback_data": d} for (t, d) in row] for row in rows]})


MENU = [[("▶️ Quiz", "quiz"), ("⚡ Blits", "blitz")],
        [("📈 Progress", "progress"), ("🏅 Nishon", "badges")],
        [("📚 Mavzu", "topic"), ("📊 Daraja", "stats")],
        [("⏸️ To'xta", "stop"), ("🔄 Reset", "reset")],
        [("❓ Yordam", "help")]]


def menu_kb():
    return kb(MENU)


def topic_menu_kb(con):
    learned = sorted(profile.learned_topics(con))
    rows, row = [], []
    for t in learned:
        row.append((f"{TOPIC_EMOJI.get(t, '•')} {t}", f"topic:{t}"))
        if len(row) == 2:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([("🔁 Kunlik (default)", "daily")])
    return kb(rows)


def stats_msg(con):
    level, _ = get_level(con)
    r = con.execute("SELECT COUNT(*) n, SUM(correct) ok FROM attempts "
                    "WHERE date(ts)=date('now')").fetchone()
    n, ok = r["n"] or 0, r["ok"] or 0
    streak = profile.streak_days(con)
    topics = ", ".join(sorted(_pool_topics(con))) or "umumiy"
    return (f"📊 <b>Holat</b>\n"
            f"Daraja: <b>{level}</b>  ·  🔥 streak: {streak} kun\n"
            f"Bugun: {ok}/{n} to'g'ri\n"
            f"Mavzu: {topics}")


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


def do_quiz(con, token, chat_id, key):
    db.set_meta(con, "tg_active", "1")
    db.set_meta(con, "tg_mode", "daily")             # blits'дан chiqsa — kunlikка qaytar
    db.set_meta(con, "tg_sess_n", 0)                 # yangi sessiya hisobi
    db.set_meta(con, "tg_sess_ok", 0)
    send_msg(token, chat_id, start_banner(con), menu_kb())
    send_quiz(token, chat_id, con, key)


def do_daily(con, token, chat_id, key):
    db.set_meta(con, "tg_topic", "")                 # override'ni tozalab, kunlikка qaytar
    do_quiz(con, token, chat_id, key)


def do_stop(con, token, chat_id):
    db.set_meta(con, "tg_active", "0")
    db.set_meta(con, "tg_mode", "daily")
    n = int(db.get_meta(con, "tg_sess_n", "0") or 0)
    ok = int(db.get_meta(con, "tg_sess_ok", "0") or 0)
    tail = f"\n📊 Bu sessiya: <b>{ok}/{n}</b> ({100 * ok // n}%)" if n else ""
    send_msg(token, chat_id, "⏸️ Quiz to'xtatildi." + tail, menu_kb())


def do_progress(con, token, chat_id):
    """O'quvchi holati: kun, streak, bugungi natija, o'rganilgan mavzular."""
    p = profile.build(con)
    r = con.execute("SELECT COUNT(*) n, SUM(correct) ok FROM attempts "
                    "WHERE date(ts)=date('now')").fetchone()
    n, ok = r["n"] or 0, r["ok"] or 0
    learned = ", ".join(p["learned"]) or "—"
    msg = ("📈 <b>Progress</b>\n"
           f"📅 Day {p['day']}/56  ·  ✅ tugatilgan: {p['done_days']} kun\n"
           f"🔥 Streak: <b>{p['streak']}</b> kun\n"
           f"🎲 Bugun quiz: {ok}/{n} to'g'ri\n"
           f"🧠 SRS takror kutyapti: {p['due']} ta\n"
           f"📚 O'rganilgan: {learned}")
    send_msg(token, chat_id, msg, menu_kb())


def do_today_info(con, token, chat_id):
    """Bugungi kun mavzusi."""
    day = int(db.get_meta(con, "current_day", "1"))
    theme = ""
    tj = os.path.join(db.DEVOPS_HOME, f"days/day-{day:02d}/tasks.json")
    if os.path.exists(tj):
        try:
            theme = json.load(open(tj, encoding="utf-8")).get("theme", "")
        except Exception:
            pass
    send_msg(token, chat_id,
             f"📅 <b>Bugun — Day {day}/56</b>\n{theme}\n\n"
             "Terminalда:  <code>devops next</code>\nBu yerда:  /quiz bilan mashq qil.",
             menu_kb())


def do_reset(con, token, chat_id):
    lv = available_levels(con)
    db.set_meta(con, "tg_level", lv[0] if lv else 1)
    db.set_meta(con, "tg_correct", 0)
    db.set_meta(con, "tg_wrong", 0)
    send_msg(token, chat_id, "🔄 Daraja boshiga qaytarildi.", menu_kb())


def do_topic_menu(con, token, chat_id):
    send_msg(token, chat_id, "📚 Qaysi mavzu? (o'rganilganlardan tanla)", topic_menu_kb(con))


def do_set_topic(con, token, chat_id, key, name):
    if name in set(profile.learned_topics(con)):
        db.set_meta(con, "tg_topic", name)
        send_msg(token, chat_id, f"✅ Mavzu tanlandi: <b>{name}</b>", menu_kb())
        send_quiz(token, chat_id, con, key)
    else:
        do_topic_menu(con, token, chat_id)


# ───────── 🏅 Nishonlar (achievements) ─────────
# (kalit, emoji, sarlavha, shart(stats)->bool)
BADGES = [
    ("streak3",  "🔥", "Olov yondi (3 kun)",        lambda s: s["streak"] >= 3),
    ("streak7",  "🔥", "Bir hafta intizom (7 kun)",  lambda s: s["streak"] >= 7),
    ("streak14", "🔥", "Ikki hafta (14 kun)",        lambda s: s["streak"] >= 14),
    ("streak30", "🏆", "Bir oy temir intizom (30 kun)", lambda s: s["streak"] >= 30),
    ("ans50",    "🎯", "50 savol javob berding",      lambda s: s["total"] >= 50),
    ("ans100",   "🎯", "100 savol",                   lambda s: s["total"] >= 100),
    ("ans250",   "🎯", "250 savol",                   lambda s: s["total"] >= 250),
    ("ans500",   "💎", "500 savol — usta",            lambda s: s["total"] >= 500),
    ("perfect",  "💯", "Mukammal sessiya (5+ savol, 0 xato)",
     lambda s: s["sess_n"] >= 5 and s["sess_ok"] == s["sess_n"]),
    ("maxlevel", "⭐", "Eng yuqori darajaga yetding",  lambda s: s["at_max"]),
    ("blitz10",  "⚡", "Blits: 10/10 mukammal",        lambda s: s["blitz_perfect"]),
]


def _stats_for_badges(con, sess_n=None, sess_ok=None, blitz_perfect=False):
    level, levels = get_level(con)
    if sess_n is None:
        sess_n = int(db.get_meta(con, "tg_sess_n", "0") or 0)
    if sess_ok is None:
        sess_ok = int(db.get_meta(con, "tg_sess_ok", "0") or 0)
    return {
        "streak": profile.streak_days(con),
        "total": con.execute("SELECT COUNT(*) FROM attempts").fetchone()[0],
        "at_max": bool(levels) and level >= levels[-1],
        "sess_n": sess_n, "sess_ok": sess_ok, "blitz_perfect": blitz_perfect,
    }


def _unlocked_set(con):
    try:
        return set(json.loads(db.get_meta(con, "tg_badges", "[]") or "[]"))
    except Exception:
        return set()


def check_and_announce(con, token, chat_id, **kw):
    """Yangi ochilgan nishonni tekshirib, Telegram'ga tabrik yuboradi."""
    unlocked = _unlocked_set(con)
    stats = _stats_for_badges(con, **kw)
    new = []
    for key, emoji, title, cond in BADGES:
        if key not in unlocked:
            try:
                if cond(stats):
                    unlocked.add(key)
                    new.append((emoji, title))
            except Exception:
                pass
    if new:
        db.set_meta(con, "tg_badges", json.dumps(sorted(unlocked)))
        body = "\n".join(f"{e} <b>{t}</b>" for e, t in new)
        send_msg(token, chat_id, f"🎉 <b>Yangi nishon ochildi!</b>\n{body}")


def do_badges(con, token, chat_id):
    unlocked = _unlocked_set(con)
    lines = [f"{'✅' if k in unlocked else '🔒'} {e} {t}" for (k, e, t, _) in BADGES]
    send_msg(token, chat_id,
             f"🏅 <b>Nishonlar</b>  ·  {len(unlocked)}/{len(BADGES)}\n" + "\n".join(lines),
             menu_kb())


# ───────── ⚡ Blits rejimi (10 savollik sprint) ─────────
BLITZ_N = 10


def do_blitz(con, token, chat_id, key):
    db.set_meta(con, "tg_mode", "blitz")
    db.set_meta(con, "tg_active", "1")
    db.set_meta(con, "tg_blitz_left", BLITZ_N)
    db.set_meta(con, "tg_blitz_ok", 0)
    send_msg(token, chat_id,
             f"⚡ <b>BLITS boshlandi!</b>\n{BLITZ_N} ta savol ketma-ket — daraja "
             "o'zgarmaydi, oxirida ball. Tezlik + aniqlik. Ketdik! 🏁",
             menu_kb())
    send_quiz(token, chat_id, con, key)


def _blitz_medal(ok):
    if ok >= 10:
        return "🥇 OLTIN — mukammal!"
    if ok >= 8:
        return "🥈 kumush — zo'r!"
    if ok >= 6:
        return "🥉 bronza — yaxshi"
    return "💪 mashq kerak — yana urin"


def on_answer(con, token, chat_id, key, correct):
    """Poll javobidan keyingi oqim: blits yoki kunlik (adaptiv) rejim."""
    if correct is None:
        return
    mode = db.get_meta(con, "tg_mode", "daily")
    if mode == "blitz":
        left = int(db.get_meta(con, "tg_blitz_left", "0") or 0) - 1
        okc = int(db.get_meta(con, "tg_blitz_ok", "0") or 0) + (1 if correct else 0)
        db.set_meta(con, "tg_blitz_left", max(left, 0))
        db.set_meta(con, "tg_blitz_ok", okc)
        if left <= 0:                                  # blits tugadi
            db.set_meta(con, "tg_mode", "daily")
            db.set_meta(con, "tg_active", "0")
            pct = 100 * okc // BLITZ_N
            send_msg(token, chat_id,
                     f"🏁 <b>Blits tugadi!</b>\nNatija: <b>{okc}/{BLITZ_N}</b> "
                     f"({pct}%)\n{_blitz_medal(okc)}", menu_kb())
            check_and_announce(con, token, chat_id, blitz_perfect=(okc == BLITZ_N))
        else:
            time.sleep(1)
            send_quiz(token, chat_id, con, key)
        return
    # kunlik / adaptiv rejim
    n = int(db.get_meta(con, "tg_sess_n", "0") or 0) + 1
    okc = int(db.get_meta(con, "tg_sess_ok", "0") or 0) + (1 if correct else 0)
    db.set_meta(con, "tg_sess_n", n)
    db.set_meta(con, "tg_sess_ok", okc)
    level, change = apply_result(con, correct)
    if change:
        send_msg(token, chat_id, level_msg(change, level))
    check_and_announce(con, token, chat_id)
    time.sleep(1)
    send_quiz(token, chat_id, con, key)


# ───────── 🔔 Kunlik eslatma + 🌙 streak-qo'riqchi (fon ipi) ─────────
def daily_theme(con):
    day = int(db.get_meta(con, "current_day", "1"))
    tj = os.path.join(db.DEVOPS_HOME, f"days/day-{day:02d}/tasks.json")
    if os.path.exists(tj):
        try:
            return day, json.load(open(tj, encoding="utf-8")).get("theme", "")
        except Exception:
            pass
    return day, ""


def _norm_hhmm(t):
    h, m = t.split(":")
    return f"{int(h):02d}:{m}"


def reminder_tick(con, token, chat_id):
    """Daqiqada bir marta chaqiriladi: ertalab turtki, kechqurun streak-guard."""
    if db.get_meta(con, "tg_rem_on", "1") != "1":
        return
    now = time.strftime("%H:%M")
    today = time.strftime("%Y-%m-%d")
    mt = db.get_meta(con, "tg_rem_morning", "09:00")
    et = db.get_meta(con, "tg_rem_evening", "20:30")
    # ☀️ Ertalabki turtki (mt..et oralig'ida, kuniga bir marta)
    if mt <= now < et and db.get_meta(con, "tg_rem_m_date", "") != today:
        db.set_meta(con, "tg_rem_m_date", today)
        day, theme = daily_theme(con)
        streak = profile.streak_days(con)
        send_msg(token, chat_id,
                 f"☀️ <b>Xayrli tong, {OWNER}!</b>\n"
                 f"📅 Bugun — Day {day}/56\n<i>{theme}</i>\n"
                 f"🔥 Streak: {streak} kun — bugun ham uzmaymiz!\n\n"
                 "Terminalда <code>devops next</code> · bu yerда /quiz yoki ⚡ /blitz.",
                 menu_kb())
    # 🌙 Kechki streak-guard (faqat bugun hali javob bo'lmasa)
    if now >= et and db.get_meta(con, "tg_rem_e_date", "") != today:
        db.set_meta(con, "tg_rem_e_date", today)
        n = con.execute("SELECT COUNT(*) FROM attempts WHERE date(ts)=date('now')").fetchone()[0]
        if n == 0:
            streak = profile.streak_days(con)
            warn = (f"🔥 {streak} kunlik streak'ing xavf ostida!"
                    if streak else "Bugun hali mashq qilmading.")
            send_msg(token, chat_id,
                     f"🌙 <b>Kun yakuniga oz qoldi</b>\n{warn}\n"
                     "Atigi 2 daqiqa — /quiz yoki ⚡ /blitz bilan streak'ni saqlab qol. 💪",
                     menu_kb())


def scheduler(token, chat_id):
    con = db.connect()                 # ip uchun alohida ulanish
    log("scheduler ip ishga tushdi")
    while True:
        try:
            reminder_tick(con, token, chat_id)
        except Exception as e:
            log(f"scheduler err: {e}")
        time.sleep(60)


def do_reminder_cmd(con, token, chat_id, arg):
    arg = (arg or "").strip().lower()
    if arg in ("off", "o'chir", "ochir", "0"):
        db.set_meta(con, "tg_rem_on", "0")
        send_msg(token, chat_id, "🔕 Eslatmalar o'chirildi.", menu_kb())
        return
    if arg in ("on", "yoq", "1"):
        db.set_meta(con, "tg_rem_on", "1")
    times = re.findall(r"\b([0-2]?\d:[0-5]\d)\b", arg)
    if times:
        db.set_meta(con, "tg_rem_morning", _norm_hhmm(times[0]))
        if len(times) >= 2:
            db.set_meta(con, "tg_rem_evening", _norm_hhmm(times[1]))
        db.set_meta(con, "tg_rem_on", "1")
    on = db.get_meta(con, "tg_rem_on", "1") == "1"
    status = "yoniq ✅" if on else "o'chiq 🔕"
    mt = db.get_meta(con, "tg_rem_morning", "09:00")
    et = db.get_meta(con, "tg_rem_evening", "20:30")
    send_msg(token, chat_id,
             f"🔔 <b>Eslatmalar:</b> {status}\n"
             f"☀️ Tong turtki: {mt}\n"
             f"🌙 Kech streak-guard: {et}\n\n"
             "O'zgartirish:  <code>/reminder 08:30 21:00</code>  ·  "
             "<code>/reminder off</code>", menu_kb())


def set_commands(token):
    """Telegram'ning native '/' buyruqlar menyusi."""
    cmds = [
        {"command": "quiz", "description": "▶️ Bugungi mavzu quizi"},
        {"command": "blitz", "description": "⚡ 10 savollik sprint"},
        {"command": "progress", "description": "📈 Kun, streak, natija"},
        {"command": "badges", "description": "🏅 Nishonlar"},
        {"command": "today", "description": "📅 Bugungi kun mavzusi"},
        {"command": "topic", "description": "📚 Mavzu tanlash"},
        {"command": "daily", "description": "🔁 Kunlik mavzuga qaytish"},
        {"command": "reminder", "description": "🔔 Eslatmalar (on/off/vaqt)"},
        {"command": "stop", "description": "⏸️ To'xtatish"},
        {"command": "reset", "description": "🔄 Darajani 1 ga"},
        {"command": "help", "description": "❓ Yordam"},
    ]
    try:
        api(token, "setMyCommands", {"commands": json.dumps(cmds, ensure_ascii=False)})
    except Exception as e:
        log(f"setMyCommands err: {e}")


OWNER = "Sanjar"          # bot egasi (murojaatlarга javob beruvchi)


def save_contact(con, uid, name, username):
    con.execute(
        "INSERT INTO tg_contacts(uid,name,username,msgs,last_ts) "
        "VALUES(?,?,?,1,datetime('now')) ON CONFLICT(uid) DO UPDATE SET "
        "name=excluded.name, username=excluded.username, msgs=msgs+1, last_ts=datetime('now')",
        (str(uid), name, username))
    con.commit()


def contacts(con):
    return con.execute("SELECT uid,name,username,msgs,last_ts FROM tg_contacts "
                       "ORDER BY last_ts DESC").fetchall()


def relay_to_user(token, uid, text):
    """Admin javobini foydalanuvchiga yuboradi."""
    try:
        api(token, "sendMessage", {"chat_id": uid, "text": f"💬 <b>{OWNER}</b>: {text}",
                                   "parse_mode": "HTML"})
        return True
    except Exception as e:
        log(f"relay fail uid={uid}: {e}")
        return False


def handle_admin(con, token, chat_id, key, m):
    """Admin (bot egasi) xabarlari — quiz buyruqlari + murojaat boshqaruvi."""
    text_raw = (m.get("text") or "").strip()
    text = text_raw.lower()
    # 1) Forward qilingan murojaatga REPLY qilib javob (tabiiy usul)
    rt = m.get("reply_to_message") or {}
    if text_raw and not text_raw.startswith("/"):
        mm = re.search(r"🆔\s*(\d+)", rt.get("text", "") or "")
        if mm:
            uid = mm.group(1)
            ok = relay_to_user(token, uid, text_raw)
            send_msg(token, chat_id, f"{'✅' if ok else '❌'} {uid} ga javob "
                                     f"{'yuborildi' if ok else 'yuborilmadi'}.")
            return
    # 2) Buyruqlar
    if text in ("/start", "/quiz", "/next"):
        do_quiz(con, token, chat_id, key)
    elif text in ("/blitz", "/blic", "/blits"):
        do_blitz(con, token, chat_id, key)
    elif text in ("/badges", "/nishon", "/nishonlar"):
        do_badges(con, token, chat_id)
    elif text.startswith("/reminder") or text.startswith("/eslatma"):
        parts = text_raw.split(maxsplit=1)
        do_reminder_cmd(con, token, chat_id, parts[1] if len(parts) >= 2 else "")
    elif text == "/daily":
        do_daily(con, token, chat_id, key)
    elif text.startswith("/topic"):
        parts = text.split()
        do_set_topic(con, token, chat_id, key, parts[1]) if len(parts) >= 2 else do_topic_menu(con, token, chat_id)
    elif text == "/stop":
        do_stop(con, token, chat_id)
    elif text in ("/progress", "/holat"):
        do_progress(con, token, chat_id)
    elif text in ("/today", "/kun"):
        do_today_info(con, token, chat_id)
    elif text == "/reset":
        do_reset(con, token, chat_id)
    elif text.startswith("/reply"):
        parts = text_raw.split(maxsplit=2)
        if len(parts) >= 3:
            ok = relay_to_user(token, parts[1], parts[2])
            send_msg(token, chat_id, f"{'✅' if ok else '❌'} {parts[1]} ga javob yuborildi.")
        else:
            send_msg(token, chat_id, "Format:  /reply &lt;id&gt; &lt;matn&gt;")
    elif text == "/users":
        rows = contacts(con)
        if not rows:
            send_msg(token, chat_id, "Hali murojaat yo'q.")
        else:
            body = "\n".join(f"🆔 <code>{r['uid']}</code> — {r['name']} "
                             f"(@{r['username'] or '-'}) · {r['msgs']} xabar" for r in rows[:30])
            send_msg(token, chat_id, "👥 <b>Murojaatchilar</b>\n" + body)
    elif text.startswith("/broadcast"):
        parts = text_raw.split(maxsplit=1)
        if len(parts) >= 2:
            sent = 0
            for r in contacts(con):
                if relay_to_user(token, r["uid"], parts[1]):
                    sent += 1
            send_msg(token, chat_id, f"📢 {sent} ta foydalanuvchiga yuborildi.")
        else:
            send_msg(token, chat_id, "Format:  /broadcast &lt;matn&gt;")
    else:
        send_msg(token, chat_id, HELP, menu_kb())


def handle_stranger(con, token, admin_id, m):
    """Begona foydalanuvchi — murojaatini adminга forward qiladi."""
    frm = m.get("from", {})
    uid = str(m.get("chat", {}).get("id"))
    name = ((frm.get("first_name", "") + " " + frm.get("last_name", "")).strip()) or "Anonim"
    uname = frm.get("username", "")
    text_raw = (m.get("text") or "").strip()
    save_contact(con, uid, name, uname)
    if text_raw.lower() in ("/start", "/help", ""):
        send_msg(token, uid, f"👋 Assalomu alaykum! Bu — <b>{OWNER}</b>ning shaxsiy boti.\n"
                             "Savol yoki murojaatingizni shu yerga yozing — egasiga yetkaziladi, "
                             "tez orada javob oladi. 📩")
        if text_raw.lower() in ("/start", "/help"):
            return
    unm = f" (@{uname})" if uname else ""
    send_msg(token, admin_id, f"📨 <b>Yangi murojaat</b>\n👤 {name}{unm}\n🆔 <code>{uid}</code>\n"
                              f"💬 {text_raw}\n\nJavob: <code>/reply {uid} matn</code>  "
                              "yoki shu xabarga reply qiling.")
    send_msg(token, uid, "✅ Xabaringiz yetkazildi. Tez orada javob beramiz. 🙏")


def process(con, token, chat_id, key, u):
    if "poll_answer" in u:
        pa = u["poll_answer"]
        correct = handle_answer(con, pa["poll_id"], pa.get("option_ids", []))
        if db.get_meta(con, "tg_active", "1") == "1":
            on_answer(con, token, chat_id, key, correct)
    elif "callback_query" in u:
        cq = u["callback_query"]
        data = cq.get("data", "")
        try:
            api(token, "answerCallbackQuery", {"callback_query_id": cq["id"]})
        except Exception:
            pass
        if str(cq.get("message", {}).get("chat", {}).get("id")) != str(chat_id):
            return
        if data == "quiz":
            do_quiz(con, token, chat_id, key)
        elif data == "blitz":
            do_blitz(con, token, chat_id, key)
        elif data == "badges":
            do_badges(con, token, chat_id)
        elif data == "stop":
            do_stop(con, token, chat_id)
        elif data == "stats":
            send_msg(token, chat_id, stats_msg(con), menu_kb())
        elif data == "progress":
            do_progress(con, token, chat_id)
        elif data == "reset":
            do_reset(con, token, chat_id)
        elif data == "help":
            send_msg(token, chat_id, HELP, menu_kb())
        elif data == "topic":
            do_topic_menu(con, token, chat_id)
        elif data == "daily":
            do_daily(con, token, chat_id, key)
        elif data.startswith("topic:"):
            do_set_topic(con, token, chat_id, key, data.split(":", 1)[1])
    elif "message" in u:
        m = u["message"]
        if str(m.get("chat", {}).get("id")) == str(chat_id):
            handle_admin(con, token, chat_id, key, m)        # bot egasi
        else:
            handle_stranger(con, token, chat_id, m)          # begona — murojaatni forward qil


def main():
    token, chat_id = load_creds()
    if not token or not chat_id:
        log("token/chat_id yo'q — chiqdim")
        sys.exit(2)
    key = load_key()
    con = db.connect()
    db.init()
    db.ensure_state(con)
    set_commands(token)                                   # native '/' buyruqlar menyusi
    threading.Thread(target=scheduler, args=(token, chat_id), daemon=True).start()
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
                "allowed_updates": json.dumps(["poll_answer", "message", "callback_query"]),
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
