"""Kunlik quiz ketma-ketligini AI bilan rejalashtiradi (zaif mavzularga urg'u).

build_plan() — bir kunlik tartiblangan rejani tuzadi (quiz_plan jadvaliga).
next_question() — rejadan keyingi savolni qaytaradi (tugasa qayta tuzadi).
Telegram quizbot shu ikkisini ishlatadi.
"""
import datetime
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402
import srs  # noqa: E402
from generate import load_key, call_api  # noqa: E402

MODEL = "claude-sonnet-4-6"
PLAN_SYSTEM = (
    "You are a DevOps curriculum planner. Output ONLY a JSON array of N objects "
    '{"topic": "...", "difficulty": 1-5} giving the ORDER of quiz questions for today. '
    "Rules: interleave topics (never 3 of the same topic in a row); weight WEAK topics "
    "about 2x; sprinkle in 'python' and 'english' every few items; progress difficulty "
    "from easy to harder; ONLY use topics from the allowed list. No prose, JSON only."
)


def weak_topics(con):
    rows = con.execute(
        "SELECT q.topic, COUNT(*) n, SUM(a.correct) ok FROM attempts a "
        "JOIN questions q ON q.id=a.question_id GROUP BY q.topic"
    ).fetchall()
    return [r["topic"] for r in rows if r["n"] >= 2 and 100 * (r["ok"] or 0) // r["n"] < 60]


def all_topics(con):
    return [r["topic"] for r in con.execute("SELECT DISTINCT topic FROM questions")]


def ai_slots(key, topics, weak, n):
    prompt = (
        f"Allowed topics: {topics}\n"
        f"WEAK topics (weight 2x): {weak or '(none yet)'}\n"
        f"N = {n}\n\nProduce the ordered JSON array."
    )
    try:
        txt = call_api(key, MODEL, prompt, system=PLAN_SYSTEM, max_tokens=2000).strip()
        if txt.startswith("```"):
            txt = txt.split("```", 2)[1].lstrip("json").strip()
        i, j = txt.find("["), txt.rfind("]")
        slots = json.loads(txt[i:j + 1])
        out = [s for s in slots if s.get("topic") in topics]
        return out or None
    except Exception:
        return None


def algo_slots(topics, weak, n):
    """AI ishlamasa: zaif mavzularni 2x og'irlik bilan aralashtirib tartiblash."""
    bag = list(topics) + list(weak)  # weak mavzular ikki marta
    random.shuffle(bag)
    slots, last = [], None
    diff_cycle = {}
    i = 0
    while len(slots) < n:
        t = bag[i % len(bag)]
        i += 1
        if t == last:  # ketma-ket bir xil mavzudan qochish
            continue
        d = diff_cycle.get(t, 0) % 3 + 1
        diff_cycle[t] = diff_cycle.get(t, 0) + 1
        slots.append({"topic": t, "difficulty": d})
        last = t
    return slots


def pick_qid(con, topic, diff, used):
    due = set(srs.due_question_ids(con, 5000))
    rows = con.execute("SELECT id FROM questions WHERE topic=? AND difficulty=?",
                       (topic, diff)).fetchall()
    cands = [r["id"] for r in rows if r["id"] not in used]
    duec = [i for i in cands if i in due]
    pool = duec or cands
    if not pool:
        rows = con.execute("SELECT id FROM questions WHERE topic=?", (topic,)).fetchall()
        pool = [r["id"] for r in rows if r["id"] not in used] or [r["id"] for r in rows]
    if not pool:
        rows = con.execute("SELECT id FROM questions").fetchall()
        pool = [r["id"] for r in rows if r["id"] not in used] or [r["id"] for r in rows]
    return random.choice(pool) if pool else None


def build_plan(con, n=40, key=None):
    db.ensure_state(con)
    key = key or load_key()
    topics = all_topics(con)
    if not topics:
        return 0
    weak = weak_topics(con)
    slots = (ai_slots(key, topics, weak, n) if key else None) or algo_slots(topics, weak, n)
    today = datetime.date.today().isoformat()
    con.execute("DELETE FROM quiz_plan WHERE date=? AND consumed=0", (today,))
    used, pos = set(), 0
    for s in slots:
        qid = pick_qid(con, s["topic"], int(s.get("difficulty", 2)), used)
        if qid is None:
            continue
        used.add(qid)
        con.execute("INSERT INTO quiz_plan(date,pos,question_id,consumed) VALUES(?,?,?,0)",
                    (today, pos, qid))
        pos += 1
    con.commit()
    return pos


def next_question(con, key=None):
    today = datetime.date.today().isoformat()
    q = """SELECT * FROM quiz_plan WHERE date=? AND consumed=0 ORDER BY pos LIMIT 1"""
    row = con.execute(q, (today,)).fetchone()
    if row is None:
        build_plan(con, key=key)              # reja tugadi yoki yo'q -> qayta tuzamiz
        row = con.execute(q, (today,)).fetchone()
    if row is None:
        return None
    con.execute("UPDATE quiz_plan SET consumed=1 WHERE id=?", (row["id"],))
    con.commit()
    return con.execute("SELECT * FROM questions WHERE id=?", (row["question_id"],)).fetchone()


if __name__ == "__main__":
    con = db.connect()
    n = build_plan(con)
    print(f"✅ Bugungi reja tuzildi: {n} ta quiz ketma-ketligi.")
    con.close()
