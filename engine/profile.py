#!/usr/bin/env python3
"""
Learner model — "bilim profili". Bitta manba: AI-coach, `devops ai`, `devops profile`
va mastery-gate shu yerdan o'qiydi. Maqsad: tizim sen haqingda XULOSA chiqarib borsin.
"""
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402

# Kurs mavzulari TARTIBI (mastery-gate ketma-ketligi). Kümülatif takror shu tartibdan oldingilarni oladi.
TOPIC_ORDER = ["linux", "bash", "git", "networking", "docker", "kubernetes"]
MASTERY_PCT = 95          # gate'dan o'tish chegarasi
MIN_ASSESSED = 10         # mavzu "baholangan" deyish uchun minimal javob soni


def topic_stats(con):
    rows = con.execute(
        "SELECT q.topic, COUNT(*) n, SUM(a.correct) ok FROM attempts a "
        "JOIN questions q ON q.id=a.question_id GROUP BY q.topic").fetchall()
    out = {}
    for r in rows:
        n = r["n"] or 0
        ok = r["ok"] or 0
        out[r["topic"]] = {"n": n, "ok": ok, "pct": (100 * ok // n) if n else 0}
    return out


def bank_counts(con):
    return {r["topic"]: r["n"] for r in
            con.execute("SELECT topic, COUNT(*) n FROM questions GROUP BY topic")}


def checkpoints_passed(con):
    try:
        return {r["topic"] for r in
                con.execute("SELECT topic FROM checkpoints WHERE passed=1")}
    except Exception:
        return set()


def streak_days(con):
    """Bugundan (yoki kechadan) orqaga uzluksiz nechta kun faollik bo'lgan."""
    rows = con.execute("SELECT DISTINCT date(ts) d FROM attempts").fetchall()
    s = {r["d"] for r in rows}
    if not s:
        return 0
    cur = datetime.date.today()
    if cur.isoformat() not in s:                 # bugun hali yo'q bo'lsa, kechadan boshла
        cur -= datetime.timedelta(days=1)
    streak = 0
    while cur.isoformat() in s:
        streak += 1
        cur -= datetime.timedelta(days=1)
    return streak


def build(con):
    """To'liq bilim profili (dict)."""
    db.ensure_state(con)
    day = int(db.get_meta(con, "current_day", "1"))
    done_days = con.execute(
        "SELECT COUNT(*) FROM day_progress WHERE status='done'").fetchone()[0]
    att = con.execute("SELECT COUNT(*) n, SUM(correct) ok FROM attempts").fetchone()
    n = att["n"] or 0
    ok = att["ok"] or 0
    stats = topic_stats(con)
    weak = sorted([t for t, s in stats.items() if s["n"] >= 2 and s["pct"] < 70],
                  key=lambda t: stats[t]["pct"])
    strong = sorted([t for t, s in stats.items() if s["n"] >= MIN_ASSESSED and s["pct"] >= 90],
                    key=lambda t: -stats[t]["pct"])
    try:
        import srs
        due = len(srs.due_question_ids(con, limit=9999))
    except Exception:
        due = 0
    return {
        "day": day, "done_days": done_days, "answers": n,
        "accuracy": 100 * ok // max(n, 1),
        "topics": stats, "bank": bank_counts(con),
        "weak": weak, "strong": strong,
        "passed": checkpoints_passed(con), "due": due,
        "streak": streak_days(con),
    }


def ai_text(con):
    """AI uchun ixcham matn — har muloqotда kontekstga qo'shiladi (sen haqingda data)."""
    p = build(con)
    parts = [f"O'quvchi Day {p['day']}/56 da, {p['done_days']} kun tugatgan, "
             f"streak {p['streak']} kun."]
    parts.append(f"Quiz: {p['answers']} javob, umumiy aniqlik {p['accuracy']}%.")
    if p["topics"]:
        ms = ", ".join(f"{t} {s['pct']}%" for t, s in
                       sorted(p["topics"].items(), key=lambda kv: -kv[1]["pct"]))
        parts.append(f"Mavzu mastery: {ms}.")
    if p["weak"]:
        parts.append(f"ZAIF (e'tibor ber): {', '.join(p['weak'])}.")
    if p["passed"]:
        parts.append(f"Mastery-gate o'tilgan: {', '.join(sorted(p['passed']))}.")
    if p["due"]:
        parts.append(f"SRS takror kutyapti: {p['due']} ta.")
    return " ".join(parts)


def prior_topics(topic):
    """Berilgan mavzudan OLDINGI mavzular (kümülatif takror uchun)."""
    if topic in TOPIC_ORDER:
        return TOPIC_ORDER[:TOPIC_ORDER.index(topic)]
    return []
