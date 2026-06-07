#!/usr/bin/env python3
"""
AI Coach — sening profilingni va ish loglaringni o'qib, shaxsiy coaching
xabarini yozadi (Telegram'ga yuboradi) va zaif mavzuga drill generatsiya qiladi.

Bu — API key'ning ASL qiymati: men (ustoz) yo'g'imda ham, har kuni AI sening
ma'lumotlaringni tahlil qilib, sengа moslangan maslahat beradi.

Foydalanish:
  python3 coach.py             # tahlil + Telegram'ga coaching xabari
  python3 coach.py --drills    # qo'shimcha: eng zaif mavzuga 8 ta yangi drill
  python3 coach.py --print     # Telegram'ga yubormay, ekranga chiqarish
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402
import worklog  # noqa: E402
from generate import load_key, call_api, generate as gen_questions  # noqa: E402

MODEL = "claude-sonnet-4-6"
TELEGRAM_NOTIFY = os.path.join(db.DEVOPS_HOME, "scripts", "telegram", "notify.py")

COACH_SYSTEM = (
    "You are 'Ustoz', a warm, motivating DevOps mentor for an Uzbek learner aiming "
    "to become a junior DevOps engineer in ~2 months. Speak Uzbek (latin), keep "
    "technical terms in English. Be specific and encouraging, never generic. "
    "Output ONLY the message (no preamble), 4-7 short lines, may use a few emojis "
    "and simple Telegram HTML (<b>...</b>). Address the learner as 'agent' or by tone."
)


def gather(con):
    db.ensure_state(con)
    day = int(db.get_meta(con, "current_day", "1"))
    done_days = con.execute("SELECT COUNT(*) FROM day_progress WHERE status='done'").fetchone()[0]
    att = con.execute("SELECT COUNT(*) n, SUM(correct) ok FROM attempts").fetchone()
    n, ok = att["n"] or 0, att["ok"] or 0
    rows = con.execute(
        "SELECT q.topic, COUNT(*) n, SUM(a.correct) ok FROM attempts a "
        "JOIN questions q ON q.id=a.question_id GROUP BY q.topic"
    ).fetchall()
    topics = []
    weak = []
    for r in rows:
        pct = 100 * (r["ok"] or 0) // r["n"]
        topics.append(f"{r['topic']}: {pct}% ({r['n']} ta)")
        if pct < 60:
            weak.append((pct, r["topic"]))
    weak.sort()
    act = worklog.today_activity()
    return {
        "day": day, "done_days": done_days, "answers": n,
        "accuracy": 100 * ok // max(n, 1),
        "topics": topics, "weak": [t for _, t in weak],
        "minutes_today": act["minutes"], "commands_today": act["commands"],
    }


def build_prompt(d):
    weak = ", ".join(d["weak"]) if d["weak"] else "(hozircha aniq zaif mavzu yo'q)"
    topics = "; ".join(d["topics"]) if d["topics"] else "(hali quiz yo'q)"
    return (
        "Learner data:\n"
        f"- Kun: {d['day']}/56, tugatilgan kunlar: {d['done_days']}\n"
        f"- Quiz javoblari: {d['answers']}, umumiy aniqlik: {d['accuracy']}%\n"
        f"- Mavzular bo'yicha: {topics}\n"
        f"- ZAIF mavzular: {weak}\n"
        f"- Bugun ishlangan: {d['minutes_today']} daqiqa, {d['commands_today']} buyruq\n\n"
        "Shu ma'lumotlarga asoslanib, bugun uchun qisqa, aniq va ilhomlantiruvchi "
        "coaching xabari yoz. Eng zaif mavzuga e'tibor qaratishni ayt va bitta "
        "amaliy maslahat ber."
    )


def main():
    args = sys.argv[1:]
    key = load_key()
    if not key:
        print("❌ ANTHROPIC_API_KEY yo'q (engine/config.json).", file=sys.stderr)
        sys.exit(2)

    con = db.connect()
    data = gather(con)
    msg = call_api(key, MODEL, build_prompt(data), system=COACH_SYSTEM, max_tokens=600).strip()
    header = f"🤖 <b>AI Coach — Day {data['day']}/56</b>\n\n"
    full = header + msg

    if "--print" in args:
        print(full.replace("<b>", "").replace("</b>", ""))
    else:
        subprocess.run([sys.executable, TELEGRAM_NOTIFY, full], check=False)
        print("✅ Telegram'ga yuborildi. Xabar matni:\n")
        print(full.replace("<b>", "").replace("</b>", ""))

    if "--drills" in args and data["weak"]:
        weakest = data["weak"][0]
        added, _ = gen_questions(con, key, weakest, difficulty=2, n=8, model=MODEL)
        print(f"🎯 Eng zaif mavzu '{weakest}' uchun +{added} drill qo'shildi.")
    con.close()


if __name__ == "__main__":
    main()
