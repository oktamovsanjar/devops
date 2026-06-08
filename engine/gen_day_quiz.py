#!/usr/bin/env python3
"""
Kun-specifik quiz generatori. Har kunning days/day-XX/quiz.json ini O'SHA KUN
o'rgatgan mavzular doirasida (MISSION + task sarlavhalari) 30  taga to'ldiradi.
Mavjud (qo'lyozma) savollar saqlanadi; faqat yetishmaganini AI bilan qo'shadi.

Foydalanish:  python3 gen_day_quiz.py 1 2 3        # day 1,2,3 ni 30 ga
              python3 gen_day_quiz.py 3 --target 30
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402
from generate import load_key, call_api, extract_json, valid  # noqa: E402

DAYS = os.path.join(db.DEVOPS_HOME, "days")
MODEL = "claude-sonnet-4-6"

SYS = (
    "You are an expert DevOps instructor writing multiple-choice quiz questions for an "
    "Uzbek learner. CRITICAL: questions must cover ONLY the concepts explicitly present in "
    "the given lesson — do NOT introduce any topic, command or subtopic that is not in it. "
    "Rules: Uzbek (latin) text, English for commands/terms; exactly 4 options; exactly ONE "
    "correct; 'correct' = 0-based index; 'explanation' = one short WHY sentence; factually "
    "correct; difficulty 1-3. Output ONLY a valid JSON array."
)


def day_scope(day):
    base = os.path.join(DAYS, f"day-{day:02d}")
    mission = ""
    mp = os.path.join(base, "MISSION.md")
    if os.path.exists(mp):
        mission = open(mp, encoding="utf-8").read()[:3000]
    titles = []
    tj = os.path.join(base, "tasks.json")
    if os.path.exists(tj):
        for t in json.load(open(tj, encoding="utf-8"))["tasks"]:
            titles.append(t.get("title", ""))
    return mission, titles


def gen(day, target=30, batch=12):
    key = load_key()
    if not key:
        print("❌ API key yo'q"); return
    base = os.path.join(DAYS, f"day-{day:02d}")
    qf = os.path.join(base, "quiz.json")
    existing = json.load(open(qf, encoding="utf-8")) if os.path.exists(qf) else []
    have = {q["q"].strip().lower() for q in existing}
    if len(existing) >= target:
        print(f"  day {day}: allaqachon {len(existing)} (>= {target})"); return
    mission, titles = day_scope(day)
    start = len(existing)
    attempts = 0
    while len(existing) < target and attempts < 8:        # bo'lib-bo'lib (token limitiga sig'sin)
        attempts += 1
        ask = min(batch, target - len(existing)) + 3
        prompt = (
            f"Day {day} lesson. Generate {ask} NEW multiple-choice questions STRICTLY within the "
            f"concepts of THIS lesson only (nothing outside it). Vary subtopics; spread difficulty 1-3.\n\n"
            f"TASK TITLES: {titles}\n\nLESSON (MISSION.md):\n{mission}\n\n"
            'JSON array. Each item: {"q":"..","options":["","","",""],"correct":0,"difficulty":1,"explanation":".."}'
        )
        try:
            items = extract_json(call_api(key, MODEL, prompt, system=SYS, max_tokens=4096))
        except Exception:
            continue                                       # bu urinish JSON bermadi — keyingisi
        for it in items:
            if len(existing) >= target:
                break
            if not valid(it):
                continue
            q = it["q"].strip()
            if q.lower() in have:
                continue
            existing.append({"q": q, "options": it["options"], "correct": it["correct"],
                             "difficulty": int(it.get("difficulty", 1)),
                             "explanation": it.get("explanation", "")})
            have.add(q.lower())
    json.dump(existing, open(qf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  day {day}: +{len(existing) - start} -> {len(existing)} savol")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("days", nargs="+", type=int)
    ap.add_argument("--target", type=int, default=30)
    a = ap.parse_args()
    for d in a.days:
        gen(d, a.target)


if __name__ == "__main__":
    main()
