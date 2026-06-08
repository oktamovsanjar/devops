#!/usr/bin/env python3
"""
Learner model — "bilim profili". Bitta manba: AI-coach, `devops ai`, `devops profile`
va mastery-gate shu yerdan o'qiydi.

MUHIM tamoyil (foydalanuvchi talabi):
  • "Bilim darajasi" (mastery) FAQAT o'rganilgan mavzu + kunlikdan KEYIN topshirilgan
    CHECKPOINT (hintsiz, 95% gate) dan chiqadi.
  • Random/Telegram "umumiy quiz" — bu MASHQ (practice). Yodlab bo'ladi, shuning uchun
    bilim darajasiga KIRMAYDI (faqat SRS/takror uchun ishlatiladi).
  • Hali o'rganilmagan mavzu (masalan kubernetes) profilда umuman ko'rinmaydi.
"""
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402

# Kurs jadvali (haftadagi mavzular) — yagona manba. cli.py ham shuni ishlatadi.
WEEK_TOPICS = {
    1: ["linux"],
    2: ["bash", "git", "networking"],
    3: ["docker"],
    4: ["cicd"],
    5: ["kubernetes"],
    6: ["kubernetes"],
    7: ["terraform", "ansible", "aws"],
    8: ["monitoring"],
}

# Checkpoint kümülatif takror tartibi
TOPIC_ORDER = ["linux", "bash", "git", "networking", "docker", "cicd", "kubernetes"]
MASTERY_PCT = 95          # gate'dan o'tish chegarasi


def current_week(day):
    return (day - 1) // 7 + 1


def learned_topics(con):
    """Shu kungacha (joriy haftani ham qo'shib) kunliklarда o'rganilgan mavzular."""
    day = int(db.get_meta(con, "current_day", "1"))
    out = []
    for w in range(1, current_week(day) + 1):
        for t in WEEK_TOPICS.get(w, []):
            if t not in out:
                out.append(t)
    return out


def set_unlock_markers(con, learned):
    """Mavzu birinchi marta 'o'rganilgan' bo'lganда vaqtni belgilaydi.
    Mashq hisobi shu vaqtdan KEYINGI javoblarga qaraladi (kunlikdan keyin)."""
    now = datetime.datetime.now().isoformat(timespec="seconds")
    for t in learned:
        if db.get_meta(con, f"unlocked:{t}") is None:
            db.set_meta(con, f"unlocked:{t}", now)


def checkpoint_mastery(con):
    """Har mavzu bo'yicha ENG SO'NGGI checkpoint natijasi."""
    try:
        rows = con.execute(
            "SELECT c.topic, c.pct, c.passed FROM checkpoints c JOIN "
            "(SELECT topic, MAX(id) mid FROM checkpoints GROUP BY topic) m ON c.id=m.mid"
        ).fetchall()
    except Exception:
        return {}
    return {r["topic"]: {"pct": r["pct"], "passed": bool(r["passed"])} for r in rows}


def post_lesson_practice(con, topic, since):
    """Mavzu o'rganilgandan KEYINGI mashq aniqligi (informativ, gate emas)."""
    if not since:
        return {"n": 0, "ok": 0, "pct": 0}
    r = con.execute(
        "SELECT COUNT(*) n, SUM(a.correct) ok FROM attempts a "
        "JOIN questions q ON q.id=a.question_id WHERE q.topic=? AND a.ts>=?",
        (topic, since)).fetchone()
    n = r["n"] or 0
    ok = r["ok"] or 0
    return {"n": n, "ok": ok, "pct": (100 * ok // n) if n else 0}


def streak_days(con):
    """Bugundan (yoki kechadan) orqaga uzluksiz nechta kun faollik bo'lgan."""
    s = {r["d"] for r in con.execute("SELECT DISTINCT date(ts) d FROM attempts")}
    if not s:
        return 0
    cur = datetime.date.today()
    if cur.isoformat() not in s:
        cur -= datetime.timedelta(days=1)
    streak = 0
    while cur.isoformat() in s:
        streak += 1
        cur -= datetime.timedelta(days=1)
    return streak


def build(con):
    """To'liq bilim profili (dict). Mastery = o'rganilgan mavzu + checkpoint."""
    db.ensure_state(con)
    day = int(db.get_meta(con, "current_day", "1"))
    done_days = con.execute(
        "SELECT COUNT(*) FROM day_progress WHERE status='done'").fetchone()[0]
    learned = learned_topics(con)
    set_unlock_markers(con, learned)
    cp = checkpoint_mastery(con)

    mastery = {}
    for t in learned:
        if t in cp:
            mastery[t] = {"assessed": True, "pct": cp[t]["pct"],
                          "passed": cp[t]["passed"], "practice": None}
        else:
            pr = post_lesson_practice(con, t, db.get_meta(con, f"unlocked:{t}"))
            mastery[t] = {"assessed": False, "pct": None, "passed": False, "practice": pr}

    passed = [t for t in learned if mastery[t]["assessed"] and mastery[t]["passed"]]
    unassessed = [t for t in learned if not mastery[t]["assessed"]]
    weak = [t for t in learned if mastery[t]["assessed"] and not mastery[t]["passed"]]

    # umumiy mashq (informativ, bilim darajasi EMAS)
    pa = con.execute("SELECT COUNT(*) n, SUM(correct) ok FROM attempts").fetchone()
    practice_total = pa["n"] or 0
    try:
        import srs
        due = len(srs.due_question_ids(con, limit=9999))
    except Exception:
        due = 0
    return {
        "day": day, "done_days": done_days, "learned": learned,
        "mastery": mastery, "passed": passed, "unassessed": unassessed, "weak": weak,
        "practice_total": practice_total, "due": due, "streak": streak_days(con),
    }


def ai_text(con):
    """AI uchun ixcham matn — har muloqotда kontekstga qo'shiladi (sen haqingda data)."""
    p = build(con)
    parts = [f"O'quvchi Day {p['day']}/56, {p['done_days']} kun tugatgan, streak {p['streak']} kun."]
    parts.append(f"O'rganilgan mavzular: {', '.join(p['learned']) or '—'}.")
    st = []
    for t in p["learned"]:
        m = p["mastery"][t]
        if m["assessed"]:
            st.append(f"{t} checkpoint {m['pct']}%" + ("✓" if m["passed"] else " (yiqildi)"))
        else:
            st.append(f"{t} hali checkpoint topshirmagan")
    if st:
        parts.append("Bilim darajasi (checkpoint): " + "; ".join(st) + ".")
    if p["weak"]:
        parts.append(f"Gate yiqilgan: {', '.join(p['weak'])}.")
    parts.append(f"(Mashq: {p['practice_total']} random javob — bilim darajasi emas, faqat takror.)")
    if p["due"]:
        parts.append(f"SRS takror: {p['due']} ta.")
    return " ".join(parts)


def prior_topics(topic):
    """Berilgan mavzudan OLDINGI mavzular (checkpoint kümülatif takror uchun)."""
    if topic in TOPIC_ORDER:
        return TOPIC_ORDER[:TOPIC_ORDER.index(topic)]
    return []
