"""Spaced Repetition (SM-2 soddalashtirilgan) — unutmaslik mexanizmi.

Har savol javob berilgach jadvalga tushadi:
- To'g'ri javob  -> interval o'sadi (1, 3, keyin ease bo'yicha), keyinroq qaytadi
- Xato javob     -> interval 1 kunga tushadi (lapse), tezroq qaytadi
Bu — Anki tizimi falsafasi: bilganingni kamroq, bilmaganingni ko'proq takrorlaysan.
"""
from datetime import date, timedelta

MIN_EASE = 1.3
MAX_EASE = 2.8


def next_state(ease, interval, reps, lapses, correct):
    if correct:
        reps += 1
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 3
        else:
            interval = max(1, round(interval * ease))
        ease = min(MAX_EASE, ease + 0.10)
    else:
        reps = 0
        interval = 1
        lapses += 1
        ease = max(MIN_EASE, ease - 0.20)
    due = (date.today() + timedelta(days=interval)).isoformat()
    return {"ease": round(ease, 2), "interval": interval, "reps": reps,
            "lapses": lapses, "due": due}


def record_answer(con, question_id, correct, chosen=None):
    """Javobni yozadi + SRS holatini yangilaydi."""
    con.execute(
        "INSERT INTO attempts(question_id, correct, chosen) VALUES(?,?,?)",
        (question_id, 1 if correct else 0, chosen),
    )
    row = con.execute(
        "SELECT ease, interval, reps, lapses FROM srs WHERE question_id=?",
        (question_id,),
    ).fetchone()
    if row is None:
        ease, interval, reps, lapses = 2.5, 0, 0, 0
    else:
        ease, interval, reps, lapses = row["ease"], row["interval"], row["reps"], row["lapses"]

    s = next_state(ease, interval, reps, lapses, correct)
    con.execute(
        "INSERT INTO srs(question_id, ease, interval, reps, lapses, due, last_review)"
        " VALUES(?,?,?,?,?,?,date('now'))"
        " ON CONFLICT(question_id) DO UPDATE SET"
        " ease=excluded.ease, interval=excluded.interval, reps=excluded.reps,"
        " lapses=excluded.lapses, due=excluded.due, last_review=date('now')",
        (question_id, s["ease"], s["interval"], s["reps"], s["lapses"], s["due"]),
    )
    con.commit()
    return s


def due_question_ids(con, limit=20):
    """Bugun takrorlash kerak bo'lgan (due <= bugun) savollar."""
    rows = con.execute(
        "SELECT question_id FROM srs WHERE due <= date('now') ORDER BY due ASC LIMIT ?",
        (limit,),
    ).fetchall()
    return [r["question_id"] for r in rows]


def due_count(con):
    return con.execute(
        "SELECT COUNT(*) FROM srs WHERE due <= date('now')"
    ).fetchone()[0]
