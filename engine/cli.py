#!/usr/bin/env python3
"""
DevOps Bootcamp — interaktiv terminal runner.

  KUNLIK OQIM:  devops next  ->  (ishni bajar)  ->  devops verify   (kun avtomatik yakunlanadi)

  devops today                # bugun nima qilaman? (kun avtomatik boshlanadi)
  devops next / verify        # keyingi ish / tekshirish (flag va qo'lda ham shu yerda)
  devops task [N]             # topshiriqlar ro'yxati / batafsil
  devops ai ["savol/mavzu"]   # AI: javob/tushuncha/shpargalka yoki bo'sh = loglardan
  devops focus / quiz / review / exam / interview   # mashq
  devops roadmap / profile / rank / deadline / stats / doctor

(.bashrc ga `alias devops='python3 ~/devops/engine/cli.py'` qo'shilgan.)
"""
import argparse
import json
import os
import random
import re
import subprocess
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Samarkand")
except Exception:
    TZ = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402
import srs  # noqa: E402
import worklog  # noqa: E402
import profile as learner  # noqa: E402  (bilim profili — learner model)
from generate import load_key, call_api  # noqa: E402

TOTAL_DAYS = 56
AI_MODEL = "claude-sonnet-4-6"

HINT_SYSTEM = (
    "You are 'Ustoz', a DevOps tutor. Give a SHORT hint (2-3 lines) in Uzbek (latin, "
    "English tech terms) that helps the learner UNDERSTAND the concept behind the quiz "
    "question. Do NOT reveal or name the correct option. End with a small guiding nudge."
)
AI_HELP_SYSTEM = (
    "You are 'Ustoz', a DevOps mentor watching the learner's terminal. From their recent "
    "commands, infer what they're doing and give a SHORT (3-5 lines) Uzbek reply: are they "
    "on track, one concrete tip, and one warning if something looks risky/wrong. Be "
    "specific to the actual commands. Tech terms in English. No preamble."
)


def ai_hint(question, topic):
    """Quiz ichida '?' bosilganda: mavzu haqida qisqa tushuncha (javobni aytmaydi)."""
    key = load_key()
    if not key:
        print(c("  ⚠️  AI yordam uchun API key kerak (engine/config.json).", "yellow"))
        return
    print(c("  🤔 Ustoz o'ylayapti...", "dim"))
    try:
        txt = call_api(
            key, AI_MODEL,
            f"Mavzu: {topic}\nSavol: {question}\n\nQisqa tushuncha ber (to'g'ri javobni aytma).",
            system=HINT_SYSTEM, max_tokens=250,
        ).strip()
        print(c("  💡 " + txt.replace("\n", "\n     "), "cyan"))
    except Exception as e:
        print(c(f"  ⚠️  AI yordam olinmadi: {e}", "yellow"))

C = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "green": "\033[32m", "red": "\033[31m", "yellow": "\033[33m",
    "cyan": "\033[36m", "mag": "\033[35m",
}


def c(txt, color):
    return f"{C[color]}{txt}{C['reset']}"


def fetch(con, ids):
    if not ids:
        return []
    qmarks = ",".join("?" * len(ids))
    rows = con.execute(
        f"SELECT * FROM questions WHERE id IN ({qmarks})", ids
    ).fetchall()
    by_id = {r["id"]: r for r in rows}
    return [by_id[i] for i in ids if i in by_id]


def _filter_clause(topic=None, category=None, topics=None):
    where, params = [], []
    if topics:
        where.append(f"topic IN ({','.join('?'*len(topics))})"); params += list(topics)
    elif topic:
        where.append("topic=?"); params.append(topic)
    if category:
        where.append("category=?"); params.append(category)
    return (("WHERE " + " AND ".join(where)) if where else ""), params


def pick_questions(con, n, topic=None, category=None, topics=None):
    clause, params = _filter_clause(topic, category, topics)
    rows = con.execute(
        f"SELECT id FROM questions {clause} ORDER BY RANDOM() LIMIT ?", (*params, n)
    ).fetchall()
    return fetch(con, [r["id"] for r in rows])


def ask(con, q, hint=True):
    """Bitta savolni interaktiv beradi. Variantlar ARALASHTIRILADI.
    hint=False -> AI yordam o'chiq (imtihon/checkpoint rejimi).
    (correct_bool, quit_bool) qaytaradi."""
    opts = json.loads(q["options"])
    order = list(range(len(opts)))
    random.shuffle(order)                  # har safar variantlar tartibi o'zgaradi
    display = [opts[i] for i in order]
    correct_pos = order.index(q["correct"])  # to'g'ri javob endi qaysi pozitsiyada
    print()
    print(c(f"  [{q['topic']} · daraja {q['difficulty']}]", "dim"))
    print(c(f"  {q['question']}", "bold"))
    for i, o in enumerate(display):
        print(f"    {c(chr(97+i), 'cyan')}) {o}")
    prompt = ("  Javob (a/b/c/d · ?=AI yordam · q=chiqish): " if hint
              else "  Javob (a/b/c/d · q=chiqish)  [HINTSIZ]: ")
    while True:
        try:
            raw = input(c(prompt, "yellow")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None, True
        if raw in ("q", "quit", "exit"):
            return None, True
        if hint and raw in ("?", "yordam", "help"):
            ai_hint(q["question"], q["topic"])
            continue
        if len(raw) == 1 and raw.isalpha():
            chosen = ord(raw) - 97
        elif raw.isdigit():
            chosen = int(raw) - 1
        else:
            chosen = -1
        break
    correct = (chosen == correct_pos)
    if correct:
        print(c("  ✅ To'g'ri!", "green"))
    else:
        right = f"{chr(97+correct_pos)}) {display[correct_pos]}"
        print(c(f"  ❌ Noto'g'ri. To'g'ri javob: {right}", "red"))
    if q["explanation"]:
        print(c(f"  💡 {q['explanation']}", "dim"))
    srs.record_answer(con, q["id"], correct, chosen)
    return correct, False


def run_session(con, questions, title):
    if not questions:
        print(c("\n  ⚠️  Bu mavzuda hali savol yo'q. `devops count` bilan tekshir yoki "
                "AI generator bilan to'ldiramiz.\n", "yellow"))
        return
    print(c(f"\n══════ {title} ({len(questions)} savol) ══════", "mag"))
    correct = total = 0
    for q in questions:
        ok, quit_ = ask(con, q)
        if quit_:
            break
        total += 1
        correct += 1 if ok else 0
    if total:
        pct = 100 * correct // total
        print(c(f"\n  📊 Natija: {correct}/{total}  ({pct}%)", "bold"))
        if pct >= 80:
            print(c("  🔥 Zo'r! Davom et.", "green"))
        elif pct >= 50:
            print(c("  💪 Yaxshi, lekin takror kerak. SRS qaytaradi.", "yellow"))
        else:
            print(c("  📚 Bu mavzuni qaytadan ko'rib chiqaylik.", "red"))
    print()


def all_ids(con, topic=None, category=None, topics=None):
    clause, params = _filter_clause(topic, category, topics)
    return [r["id"] for r in con.execute(f"SELECT id FROM questions {clause}", params)]


class AdaptivePicker:
    """Adaptiv qiyinlik. Eng past darajadan boshlaydi; ketma-ket 2 to'g'ri ->
    daraja oshadi; ketma-ket 2 xato -> tushadi (takror). Orada past darajalardan
    Daraja FAQAT joriy daraja savollariga qarab o'zgaradi. 'q' bosguncha cheksiz."""

    PROMOTE = 2   # ketma-ket nechta to'g'ridan keyin daraja oshadi
    DEMOTE = 2    # ketma-ket nechta xatodan keyin daraja tushadi

    def __init__(self, con, topic=None, category=None, topics=None):
        self.con = con
        clause, params = _filter_clause(topic, category, topics)
        rows = con.execute(
            f"SELECT id, difficulty FROM questions {clause}", params).fetchall()
        self.by_diff = defaultdict(list)
        for r in rows:
            self.by_diff[r["difficulty"]].append(r["id"])
        self.levels = sorted(self.by_diff)
        self.level = self.levels[0] if self.levels else 1
        self.correct_streak = self.wrong_streak = 0
        self.recent = deque(maxlen=20)

    def next(self):
        """Savol DOIM joriy darajada (eng yaqin mavjudida) — sakrashlar yo'q."""
        if not self.levels:
            return None
        d = min(self.levels, key=lambda x: (abs(x - self.level), x))
        pool = [i for i in self.by_diff[d] if i not in self.recent] or self.by_diff[d]
        qid = random.choice(pool)
        self.recent.append(qid)
        rows = fetch(self.con, [qid])
        return rows[0] if rows else None

    def update(self, correct):
        """Daraja o'zgarsa ('up'|'down', yangi_daraja), aks holda None."""
        if not self.levels:
            return None
        idx = self.levels.index(self.level)
        if correct:
            self.correct_streak += 1
            self.wrong_streak = 0
            if self.correct_streak >= self.PROMOTE and idx < len(self.levels) - 1:
                self.level = self.levels[idx + 1]
                self.correct_streak = 0
                return ("up", self.level)
        else:
            self.wrong_streak += 1
            self.correct_streak = 0
            if self.wrong_streak >= self.DEMOTE and idx > 0:
                self.level = self.levels[idx - 1]
                self.wrong_streak = 0
                return ("down", self.level)
        return None


def run_continuous(con, picker, title):
    print(c(f"\n══════ {title} — ADAPTIV rejim ('q' bilan chiqasan) ══════", "mag"))
    print(c(f"  📊 Boshlang'ich daraja: {picker.level}  —  to'g'ri qilsang oshadi, "
            "xato qilsang tushadi", "dim"))
    q = picker.next()
    if q is None:
        print(c("\n  ⚠️  Bu mavzuda savol yo'q.\n", "yellow"))
        return
    correct = total = 0
    while q is not None:
        ok, quit_ = ask(con, q)
        if quit_:
            break
        total += 1
        correct += 1 if ok else 0
        change = picker.update(ok)
        if change and change[0] == "up":
            print(c(f"  📈 Zo'r! Daraja OSHDI → {change[1]}", "green"))
        elif change:
            print(c(f"  📉 Daraja tushdi → {change[1]} (mustahkamlaymiz, takror)", "yellow"))
        if total % 5 == 0:
            print(c(f"\n  ── Oraliq: {correct}/{total} · joriy daraja {picker.level} ──", "mag"))
        q = picker.next()
    if total:
        print(c(f"\n  📊 Sessiya yakuni: {correct}/{total}  ({100*correct//total}%) · "
                f"yakuniy daraja {picker.level}", "bold"))
    print()


def cmd_quiz(args):
    con = db.connect()
    topic = args.topic
    category = topics = None
    label = args.topic or "aralash"
    if topic == "today":                      # faqat bugungi kun mavzu(lar)i
        day = current_day(con)
        cand = day_topics(day)
        topics = [t for t in cand if con.execute(
            "SELECT 1 FROM questions WHERE topic=? LIMIT 1", (t,)).fetchone()]
        topic = None
        label = f"BUGUN Day {day} ({', '.join(topics) or 'umumiy'})"
        if not topics:
            print(c("\n  ℹ️  Bugungi mavzuda hali savol yo'q — umumiy rejimga o'tdim.", "yellow"))
    elif topic in ("devops", "python", "english"):
        category, topic = topic, None
    if args.n and args.n > 0:                 # cheklangan sessiya
        qs = pick_questions(con, args.n, topic=topic, category=category, topics=topics)
        run_session(con, qs, f"QUIZ — {label}")
    else:                                     # default: cheksiz ADAPTIV oqim
        run_continuous(con, AdaptivePicker(con, topic=topic, category=category, topics=topics),
                       f"QUIZ — {label}")
    con.close()


def cmd_review(args):
    con = db.connect()
    ids = srs.due_question_ids(con, limit=args.n)
    qs = fetch(con, ids)
    if not qs:
        print(c("\n  🎉 Bugun takrorlash uchun hech narsa yo'q! Hammasi yangi (due emas).\n", "green"))
    run_session(con, qs, "🧠 SRS TAKROR (eski mavzular)")
    con.close()


def checkpoint_questions(con, topic, n_topic=25, n_prior=5):
    """Mastery-gate to'plami: shu mavzudan n_topic + oldingi mavzulardan n_prior (kümülatif)."""
    prior = [t for t in learner.prior_topics(topic)
             if con.execute("SELECT 1 FROM questions WHERE topic=? LIMIT 1", (t,)).fetchone()]
    if not prior:                                  # birinchi mavzu — kümülatif yo'q
        n_topic, n_prior = n_topic + n_prior, 0
    qs = pick_questions(con, n_topic, topic=topic)
    seen = {q["id"] for q in qs}
    pri = [q for q in pick_questions(con, n_prior, topics=prior) if q["id"] not in seen] if prior else []
    allq = qs + pri
    random.shuffle(allq)
    return allq, len(qs), len(pri)


def checkpoint_finish(con, topic, correct, total):
    pct = 100 * correct // max(total, 1)
    passed = 1 if pct >= learner.MASTERY_PCT else 0
    con.execute("INSERT INTO checkpoints(topic,score,total,pct,passed) VALUES(?,?,?,?,?)",
                (topic, correct, total, pct, passed))
    con.commit()
    print(c("\n  ═══════════ MASTERY GATE ═══════════", "mag"))
    print(c(f"  {topic}:  {correct}/{total}  ({pct}%)   ·   kerak: {learner.MASTERY_PCT}%", "bold"))
    if passed:
        print(c(f"  🔓 O'TDING! '{topic}' mastery tasdiqlandi. Keyingi bosqich ochiq.", "green"))
    else:
        print(c(f"  🔒 Hali emas. Zaif joyni mustahkamla:  devops quiz {topic}", "red"))
        print(c("     SRS xato savollarni qaytaradi — keyin qayta:  devops checkpoint " + topic, "dim"))
    print()
    return bool(passed)


def cmd_checkpoint(args):
    """🎯 Mastery-gate — mavzu bo'yicha hintsiz, 95% talab qiladigan nazorat."""
    con = db.connect()
    topic = args.topic
    if not topic:                                  # default: bugungi kun mavzusi
        for t in day_topics(current_day(con)):
            if con.execute("SELECT 1 FROM questions WHERE topic=? LIMIT 1", (t,)).fetchone():
                topic = t; break
        topic = topic or "linux"
    qs, nt, npri = checkpoint_questions(con, topic)
    if len(qs) < 10:
        print(c(f"\n  ℹ️  '{topic}' uchun yetarli savol yo'q ({len(qs)} ta). "
                "Boshqa mavzu tanla yoki keyinroq.\n", "yellow"))
        con.close(); return
    print(c(f"\n  ╔══════ 🎯 MASTERY GATE — {topic} ══════╗", "mag"))
    print(c(f"  {len(qs)} savol ({nt} {topic}" + (f" + {npri} kümülatif takror)" if npri else ")")
            + f"  ·  HINTSIZ  ·  o'tish: {learner.MASTERY_PCT}%", "bold"))
    print(c("  Bu QUIZ emas — nazorat. AI yordam yo'q. 'q' = to'xtatish.", "red"))
    try:
        input(c("\n  Tayyormisan? Enter (yoki Ctrl+C bekor)... ", "yellow"))
    except (EOFError, KeyboardInterrupt):
        print(); con.close(); return
    correct = total = 0
    for i, q in enumerate(qs, 1):
        print(c(f"\n  ── {i}/{len(qs)} ──", "dim"))
        ok, quit_ = ask(con, q, hint=False)
        if quit_:
            print(c("  ⏹️ To'xtatildi.", "yellow")); break
        total += 1
        correct += 1 if ok else 0
    if total:
        checkpoint_finish(con, topic, correct, total)
    con.close()


def cmd_stats(args):
    con = db.connect()
    t, by = db.counts(con)
    att = con.execute("SELECT COUNT(*) n, SUM(correct) ok FROM attempts").fetchone()
    n, ok = att["n"] or 0, att["ok"] or 0
    today = con.execute(
        "SELECT COUNT(*) n, SUM(correct) ok FROM attempts WHERE date(ts)=date('now')"
    ).fetchone()
    tn, tok = today["n"] or 0, today["ok"] or 0
    due = srs.due_count(con)
    learning = con.execute("SELECT COUNT(*) FROM srs").fetchone()[0]
    con.close()
    print(c("\n  📊 STATISTIKA", "bold"))
    print(f"  Bank: {c(t,'cyan')} savol  {dict(by)}")
    print(f"  O'rganilayotgan (SRS): {learning}   ·   Bugun takror kerak: {c(due,'yellow')}")
    print(f"  Jami javoblar: {n}  ·  aniqlik: {c(str(100*ok//max(n,1))+'%','green')}")
    print(f"  Bugun: {tn} javob  ·  {tok} to'g'ri\n")


# ─────────── KUN BOSHQARUVI (day / task / lab / deadline) ───────────

STATUS_UZ = {"pending": "boshlanmagan", "active": "jarayonda ⏳", "done": "tugatilgan ✅"}


def now_tz():
    return datetime.now(TZ) if TZ else datetime.now()


# Hafta -> shu haftaning mavzulari (devops quiz today shu bo'yicha filtrlaydi)
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


def day_topics(day):
    return WEEK_TOPICS.get((day - 1) // 7 + 1, [])


def current_day(con):
    db.ensure_state(con)
    return int(db.get_meta(con, "current_day", "1"))


def mission_rel(day):
    return f"days/day-{day:02d}/MISSION.md"


def mission_path(day):
    return os.path.join(db.DEVOPS_HOME, mission_rel(day))


def mission_title(day):
    p = mission_path(day)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.startswith("### Mavzu:"):
                return line.replace("### Mavzu:", "").strip()
    return None


def load_tasks(day):
    p = os.path.join(db.DEVOPS_HOME, f"days/day-{day:02d}/tasks.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None


def deadline_remaining(deadline_iso):
    if not deadline_iso:
        return None
    try:
        dl = datetime.fromisoformat(deadline_iso)
    except ValueError:
        return None
    now = datetime.now(dl.tzinfo) if dl.tzinfo else datetime.now()
    mins = int((dl - now).total_seconds() // 60)
    return dl, mins


def show_dashboard(con, day):
    dp = db.get_day(con, day)
    status = dp["status"] if dp else "pending"
    act = worklog.today_activity()
    due = srs.due_count(con)
    t, _ = db.counts(con)
    data = load_tasks(day)
    title = mission_title(day) or "(mission tez orada ochiladi)"

    print(c("\n  ╔════════════════════════════════════════════╗", "mag"))
    print(c(f"  ║   📅 DAY {day:02d} / {TOTAL_DAYS}      holat: {STATUS_UZ[status]:<14} ║", "mag"))
    print(c("  ╚════════════════════════════════════════════╝", "mag"))
    print(f"  📖 {c(title, 'cyan')}")
    print(f"  📂 Mission: {mission_rel(day)}")
    print(f"  ⏱️  Bugun ishlangan: {c(str(act['minutes'])+' daqiqa', 'green')}"
          f"  ({act['commands']} buyruq)   🎯 maqsad: ~7-8 soat")
    if status == "active" and dp and dp["deadline"]:
        info = deadline_remaining(dp["deadline"])
        if info:
            _, mins = info
            if mins >= 0:
                print(f"  ⏳ Muhlat: bugun {dp['deadline'][11:16]} gacha "
                      f"({c(f'{mins//60}s {mins%60}d qoldi', 'yellow')})")
            else:
                print(c(f"  ⚠️  Muhlat o'tib ketdi! ({-mins//60}s {-mins%60}d oldin)", "red"))

    print(c("\n  📋 Bugungi ish:", "bold"))
    if data:
        tasks = data.get("tasks", [])
        done = db.done_task_ids(con, day)
        nd = sum(1 for x in tasks if x["id"] in done)
        bar = "█" * nd + "░" * (len(tasks) - nd)
        print(f"   🎯 Topshiriqlar:  devops task   [{bar}] {nd}/{len(tasks)}")
    else:
        print(f"   🎯 Topshiriqlar:  MISSION.md ni o'qi")
    print(f"   🧪 Laboratoriya:  devops lab    (ishchi papkang)")
    print(f"   🧠 SRS takror:    devops review ({c(due, 'yellow')} ta kutyapti)")
    print(f"   📲 Quiz/drill:    devops quiz   ({t} savol bankda)")

    print()
    if status == "pending":
        print(c("  ▶️  BOSHLASH:  devops start", "yellow"))
    elif status == "active":
        print(c("  🏁 TUGATGACH:  devops done", "yellow"))
    else:
        print(c("  ✅ Bu kun tugadi. Keyingi kun avtomatik ochildi — devops today", "green"))
    print()


def _auto_start(con, day):
    """Kun AVTOMATIK boshlanadi (alohida 'start' buyrug'i kerak emas)."""
    dp = db.get_day(con, day)
    if dp is None or dp["status"] == "pending":
        now = now_tz()
        deadline = now.replace(hour=23, minute=59, second=0, microsecond=0)
        db.upsert_day(con, day, status="active",
                      started_at=now.isoformat(timespec="seconds"),
                      deadline=deadline.isoformat(timespec="seconds"))


def _auto_complete(con, day, tasks):
    """Barcha topshiriq bajarilsa, kun AVTOMATIK yakunlanadi va keyingisi ochiladi."""
    done = db.done_task_ids(con, day)
    if not (tasks and all(t["id"] in done for t in tasks)):
        return False
    dp = db.get_day(con, day)
    if not dp or dp["status"] != "done":
        db.upsert_day(con, day, status="done",
                      completed_at=now_tz().isoformat(timespec="seconds"))
        if day < TOTAL_DAYS:
            db.set_meta(con, "current_day", day + 1)
    return True


def cmd_today(args):
    con = db.connect()
    day = current_day(con)
    _auto_start(con, day)
    show_dashboard(con, day)
    con.close()


TASK_ICON = {"deep": "🎯", "drill": "🔁", "lab": "🧪", "track": "📚", "secret": "🔐", "real": "🏗️"}


def ensure_work(day):
    """UMUMIY QOIDA: kunning ish joyi (days/day-XX/work/) har doim mavjud bo'lsin."""
    os.makedirs(os.path.join(db.DEVOPS_HOME, "days", f"day-{day:02d}", "work"), exist_ok=True)


def _task_check(task, day):
    """Topshiriqni real tizimda avtomatik tekshiradi. True/False yoki None (auto yo'q)."""
    check = task.get("check")
    if not check:
        return None
    lab = os.path.join(db.DEVOPS_HOME, "days", f"day-{day:02d}", "work")
    os.makedirs(lab, exist_ok=True)
    env = {**os.environ, "LAB": lab,
           "DAY": os.path.join(db.DEVOPS_HOME, "days", f"day-{day:02d}")}
    try:
        return subprocess.run(["bash", "-c", check], env=env,
                              capture_output=True, timeout=15).returncode == 0
    except Exception:
        return False


def _task_detail(t, n, day, done):
    print(c(f"\n  ── Topshiriq {n}: {t['title']}  (+{t.get('xp',0)} XP)"
            + ("  ✅" if t["id"] in done else ""), "bold"))
    if t.get("why"):
        print(c(f"  💡 Nega: {t['why']}", "cyan"))
    if t.get("steps"):
        print(c("  📋 Qadamlar:", "bold"))
        for s in t["steps"]:
            print(f"     • {s}")
    if t.get("expect"):
        print(c(f"  🎯 Kutilgan natija: {t['expect']}", "dim"))
    if t.get("flag"):
        print(c(f"  📂 Quest papkasi:  ~/devops/days/day-{day:02d}/quest", "cyan"))
        print(c("  🏴 Quest'ni yech, flagni top — keyin:  devops verify", "yellow"))
    elif t.get("check"):
        print(c(f"  📂 Ish papkang:  ~/devops/days/day-{day:02d}/work", "cyan"))
        print(c("  ✅ Bajargach:  devops verify   (AI/tizim tekshiradi)", "yellow"))
    else:
        print(c("  ✅ Bajargach:  devops verify   (AI/tizim tekshiradi)", "yellow"))
    print()


def cmd_task(args):
    con = db.connect()
    day = current_day(con)
    data = load_tasks(day)
    if not data:
        print(c(f"\n  ℹ️  Day {day:02d} uchun topshiriq fayli hali yo'q.", "yellow"))
        print(f"  {mission_rel(day)} ni o'qib ishla.\n"); con.close(); return
    tasks = data.get("tasks", [])
    done = db.done_task_ids(con, day)
    a, b = args.a, args.b

    def idx(v):
        return int(v) if v and str(v).isdigit() and 1 <= int(v) <= len(tasks) else None

    if a == "done":                                   # qo'lda belgilash
        n = idx(b)
        if not n:
            print(c(f"\n  ❌ Raqam 1..{len(tasks)}. Misol: devops task done 1\n", "red"))
        else:
            db.mark_task(con, day, tasks[n - 1]["id"])
            print(c(f"\n  ✅ '{tasks[n-1]['title']}' bajarildi! (+{tasks[n-1].get('xp',0)} XP)\n", "green"))
        con.close(); return

    if a == "check":                                  # avtomatik tekshiruv
        single = idx(b)
        nums = [single] if single else range(1, len(tasks) + 1)
        print(c(f"\n  🔍 AVTO-TEKSHIRUV — Day {day:02d}", "bold"))
        passed = 0
        for n in nums:
            t = tasks[n - 1]
            res = _task_check(t, day)
            if res is None:
                kind = "flag" if t.get("flag") else "o'zing belgila"
                print(c(f"   ⏭️  {n}. {t['title']} — qo'lda ({kind})", "dim"))
            elif res:
                db.mark_task(con, day, t["id"]); passed += 1
                print(c(f"   ✅ {n}. {t['title']} — BAJARILDI (+{t.get('xp',0)} XP)", "green"))
            else:
                line = c(f"   ❌ {n}. {t['title']} — hali emas", "red")
                if single and t.get("expect"):
                    line += c(f"   (kutilgan: {t['expect']})", "dim")
                print(line)
        print(c(f"\n  {passed} ta topshiriq tasdiqlandi.\n", "yellow"))
        con.close(); return

    if idx(a):                                        # bitta topshiriq tafsiloti
        _task_detail(tasks[idx(a) - 1], idx(a), day, done)
        con.close(); return

    print(c(f"\n  📋 DAY {day:02d} TOPSHIRIQLARI", "bold"))           # ro'yxat (default)
    print(c(f"  {data.get('theme', '')}", "cyan"))
    print(c("  batafsil: devops task <raqam>  ·  tekshir: devops task check\n", "dim"))
    total = got = 0
    cur_block = None
    for i, t in enumerate(tasks, 1):
        if t.get("block") and t["block"] != cur_block:
            cur_block = t["block"]
            print(c(f"\n  ── 📦 {cur_block} ──", "mag"))
        total += t.get("xp", 0)
        is_done = t["id"] in done
        got += t.get("xp", 0) if is_done else 0
        mark = c("[✓]", "green") if is_done else "[ ]"
        tag = c(" ⚙️auto", "cyan") if t.get("check") else (c(" 🏴flag", "yellow") if t.get("flag") else "")
        print(f"  {mark} {i}. {TASK_ICON.get(t.get('type'),'•')} {c(t['title'],'bold')}  +{t.get('xp',0)}XP{tag}")
        if t.get("why"):
            print(c(f"        {t['why']}", "dim"))
    print(c(f"\n  XP: {got}/{total}\n", "yellow"))
    con.close()


def _lab_evidence(day, maxlen=3000):
    lab = os.path.join(db.DEVOPS_HOME, "days", f"day-{day:02d}", "work")
    if not os.path.isdir(lab):
        return "(ish maydoni bo'sh — hali hech narsa yaratilmagan)"
    tree, contents = [], []
    for root, dirs, files in os.walk(lab):
        rel = os.path.relpath(root, lab)
        if rel != ".":
            tree.append(rel + "/")
        for fn in sorted(files):
            fp = os.path.join(root, fn)
            r = os.path.relpath(fp, lab)
            tree.append("  " + r)
            try:
                with open(fp, encoding="utf-8", errors="ignore") as fh:
                    contents.append(f"--- {r} ---\n{fh.read(700)}")
            except Exception:
                contents.append(f"--- {r} --- (o'qib bo'lmadi)")
    txt = "Papka/fayl tuzilmasi:\n" + ("\n".join(tree) if tree else "(bo'sh)")
    if contents:
        txt += "\n\nFayl mazmunlari:\n" + "\n".join(contents)
    return txt[:maxlen]


def _task_ai_verify(task, day, shell_result):
    goal = (f"Topshiriq: {task['title']}\nMaqsad: {task.get('why','')}\n"
            f"Kutilgan natija: {task.get('expect','')}\nQadamlar: {task.get('steps','')}")
    note = "\nShell-tekshiruv: " + ("O'TDI" if shell_result is True
            else "O'TMADI" if shell_result is False else "yo'q (faqat AI baholaydi)")
    sysp = ("You are 'Ustoz' verifying a learner's hands-on task. Reply in Uzbek. The FIRST "
            "line MUST be EXACTLY 'NATIJA: PASS' or 'NATIJA: FAIL'. Then 2-4 short lines: "
            "nimasi to'g'ri, nimasi yetishmaydi (agar bo'lsa), bitta aniq maslahat. "
            "IMPORTANT: if 'Shell-tekshiruv: O'TDI', the objective requirement is already MET — "
            "give a positive confirmation (NATIJA: PASS) plus maybe a quality tip; do NOT claim "
            "files/folders are missing. Empty folders in the tree are valid. Honest, specific, "
            "encouraging. Tech terms in English.")
    ans = ai_ask(sysp, goal + note + "\n\nO'quvchi ishi (labs fayllari):\n" + _lab_evidence(day),
                 max_tokens=400)
    passed = bool(ans) and ans.strip().upper().startswith("NATIJA: PASS")
    return passed, ans


def cmd_verify(args):
    """🧠 Topshirig'ingni tekshiradi (shell+AI / flag / qo'lda). Hammasi tugasa kun yopiladi."""
    con = db.connect()
    day = current_day(con)
    _auto_start(con, day)
    data = load_tasks(day)
    if not data:
        print(c("\n  ℹ️  Topshiriq yo'q.\n", "yellow")); con.close(); return
    tasks = data["tasks"]
    done = db.done_task_ids(con, day)
    n = int(args.n) if args.n and str(args.n).isdigit() and 1 <= int(args.n) <= len(tasks) else None
    if n is None:
        pend = [(i, t) for i, t in enumerate(tasks, 1) if t["id"] not in done]
        if not pend:
            print(c("\n  🎉 Barcha topshiriqlar bajarilgan! Keyingi kun: devops today\n", "green"))
            con.close(); return
        n, task = pend[0]
    else:
        task = tasks[n - 1]

    passed = False
    if task.get("flag"):                                    # FLAG (avto-marker yoki kiritish)
        if _task_check(task, day) is True:
            passed = True
        else:
            try:
                code = input(c(f"\n  🏴 '{task['title']}' — topgan flagni kirit: ", "yellow")).strip()
            except (EOFError, KeyboardInterrupt):
                code = ""
            passed = bool(code) and code.lower() == task["flag"].strip().lower()
            if code and not passed:
                print(c("  ❌ Flag noto'g'ri.", "red"))
    else:
        shell = _task_check(task, day)
        if shell is None:                                   # qo'lda (tushuntirish) — AI baholaydi
            try:
                ans = input(c(f"\n  ✍️  '{task['title']}' — javobingni yoz: ", "yellow")).strip()
            except (EOFError, KeyboardInterrupt):
                ans = ""
            if ans:
                fb = ai_ask("You are Ustoz evaluating a learner's short answer. Reply Uzbek. FIRST "
                            "line 'NATIJA: PASS' or 'NATIJA: FAIL', then 1-2 lines feedback.",
                            f"Topshiriq: {task['title']} ({task.get('why','')})\nJavob: {ans}", max_tokens=250)
                passed = bool(fb) and fb.strip().upper().startswith("NATIJA: PASS")
                if fb:
                    print(c("  🧑‍🏫 " + "\n".join(fb.splitlines()[1:]).strip(), "cyan"))
        else:                                               # shell-check + AI fikr
            print(c(f"\n  🧠 Tekshiryapti: {task['title']}...", "dim"))
            _, fb = _task_ai_verify(task, day, shell)
            passed = shell
            if fb:
                print(c("  🧑‍🏫 " + "\n".join(fb.splitlines()[1:]).strip().replace("\n", "\n  "), "cyan"))

    if passed:
        db.mark_task(con, day, task["id"])
        print(c(f"\n  ✅ '{task['title']}' TASDIQLANDI (+{task.get('xp',0)} XP)", "green"))
        if _auto_complete(con, day, tasks):
            nxt = min(day + 1, TOTAL_DAYS)
            print(c(f"\n  🎉 DAY {day:02d} TO'LIQ YAKUNLANDI! Keyingi kun (Day {nxt:02d}) ochildi → devops today\n", "green"))
        else:
            print(c("  →  davom:  devops next\n", "yellow"))
    else:
        print(c(f"\n  ❌ Hali tayyor emas — tuzatib, qayta:  devops verify {n}\n", "red"))
    con.close()


def cmd_next(args):
    """👉 Keyingi bajariladigan topshiriqni aniq ko'rsatadi (chalkashliksiz oqim)."""
    con = db.connect()
    day = current_day(con)
    _auto_start(con, day)
    data = load_tasks(day)
    if not data:
        print(c("\n  ℹ️  Topshiriq yo'q.\n", "yellow")); con.close(); return
    tasks = data["tasks"]
    done = db.done_task_ids(con, day)
    pend = [(i, t) for i, t in enumerate(tasks, 1) if t["id"] not in done]
    if not pend:
        print(c("\n  🎉 Bugungi barcha topshiriqlar bajarildi! Keyingi kun: devops today\n", "green"))
        con.close(); return
    n, task = pend[0]
    print(c(f"\n  👉 KEYINGI ISH  ({sum(1 for t in tasks if t['id'] in done)}/{len(tasks)} bajarilgan)", "bold"))
    if task.get("block"):
        blocks = []
        for t in tasks:
            b = t.get("block", "")
            if b and (not blocks or blocks[-1] != b):
                blocks.append(b)
        bi = blocks.index(task["block"]) + 1 if task["block"] in blocks else 0
        bdone = sum(1 for t in tasks if t.get("block") == task["block"] and t["id"] in done)
        btot = sum(1 for t in tasks if t.get("block") == task["block"])
        print(c(f"  📦 Blok {bi}/{len(blocks)}: {task['block']}  ({bdone}/{btot})", "mag"))
    _task_detail(task, n, day, done)
    print(c("  Bajargach:  devops verify\n", "yellow"))
    con.close()


def cmd_deadline(args):
    con = db.connect()
    day = current_day(con)
    dp = db.get_day(con, day)
    act = worklog.today_activity()
    con.close()
    print(c(f"\n  ⏳ DAY {day:02d} — MUHLAT & VAQT", "bold"))
    if not dp or dp["status"] == "pending":
        print(c("  Kun hali boshlanmagan. `devops start` bilan boshla — muhlat o'shanda yoqiladi.\n", "yellow"))
        return
    print(f"  ⏱️  Bugun ishlangan: {c(str(act['minutes'])+' daqiqa', 'green')}"
          f"  (birinchi: {act['first'] or '—'}, oxirgi: {act['last'] or '—'})")
    if dp["deadline"]:
        info = deadline_remaining(dp["deadline"])
        if info:
            _, mins = info
            if mins >= 0:
                print(f"  ⏳ Muhlat: {dp['deadline'][11:16]} gacha — {c(f'{mins//60}s {mins%60}d qoldi', 'yellow')}")
            else:
                print(c(f"  ⚠️  Muhlat o'tdi ({-mins//60}s {-mins%60}d oldin). Tezroq `devops done`!", "red"))
    print()


def _bar(pct, width=10):
    fill = max(0, min(width, round(pct * width / 100)))
    return "█" * fill + "░" * (width - fill)


def cmd_profile(args):
    con = db.connect()
    start = db.get_meta(con, "start_date")
    p = learner.build(con)
    con.close()

    print(c("\n  🧑‍🚀 MEN HAQIMDA (Bilim profili)", "bold"))
    print(c("  — AI-coach va ustoz har muloqotда shu ma'lumotни o'qiydi —\n", "dim"))
    print(f"  Boshlangan: {start}   ·   Joriy kun: {p['day']}/{TOTAL_DAYS}   ·   Tugatilgan: {p['done_days']}")
    print(f"  🔥 Streak: {c(str(p['streak'])+' kun', 'mag')}   ·   Quiz javoblari: {p['answers']}"
          f"   ·   Aniqlik: {c(str(p['accuracy'])+'%', 'green')}")
    if p["due"]:
        print(f"  🧠 SRS takror kutyapti: {c(str(p['due'])+' ta', 'yellow')}  (devops review)")

    if p["topics"]:
        print(c("\n  Mavzu mastery (gate: 95%):", "bold"))
        order = sorted(p["topics"].items(), key=lambda kv: kv[1]["pct"])
        for t, s in order:
            pct = s["pct"]
            gate = c("🔒 gate o'tilgan", "green") if t in p["passed"] else (
                   c("⚠️ zaif", "red") if pct < 70 else (
                   c("✅ tayyor", "green") if pct >= learner.MASTERY_PCT else c("◔ o'rta", "yellow")))
            col = "green" if pct >= learner.MASTERY_PCT else ("red" if pct < 70 else "yellow")
            print(f"   {t:<11} {c(_bar(pct), col)} {pct:>3}%  ({s['ok']}/{s['n']})  {gate}")
    else:
        print(c("\n  Hali quiz ma'lumoti yo'q — boshla:  devops quiz today", "yellow"))

    if p["weak"]:
        print(c(f"\n  🎯 Tavsiya: avval shularni mustahkamla → {', '.join(p['weak'])}", "yellow"))
        print(c(f"     Mashq:  devops quiz {p['weak'][0]}   ·   Gate:  devops checkpoint {p['weak'][0]}", "dim"))
    print()


def _exam_check(check, exam_dir):
    """Topshiriq tekshiruvini bajaradi (bash). exit 0 = o'tdi. $EXAM = ish papkasi."""
    try:
        r = subprocess.run(["bash", "-c", check],
                           env={**os.environ, "EXAM": exam_dir},
                           capture_output=True, timeout=15)
        return r.returncode == 0
    except Exception:
        return False


def _exam_finish(con, name, score, maxpts, passpct):
    pct = 100 * score // max(maxpts, 1)
    passed = pct >= passpct
    con.execute("INSERT INTO exam_results(exam,score,max,passed) VALUES(?,?,?,?)",
                (name, score, maxpts, 1 if passed else 0))
    con.commit()
    print(c("\n  ═══════════════ NATIJA ═══════════════", "mag"))
    print(c(f"  Ball: {score}/{maxpts}  ({pct}%)", "bold"))
    if passed:
        print(c(f"  🎓 O'TDINGIZ! Tabriklayman, agent! (kerak edi: {passpct}%)", "green"))
    else:
        print(c(f"  ❌ O'TMADINGIZ (kerak: {passpct}%). Mashq qil va qayta urin: devops exam", "red"))
    print()


def cmd_exam(args):
    """Amaliy imtihon — hintsiz, qattiq nazorat, real tizim tekshiruvi bilan."""
    con = db.connect()
    day = current_day(con)
    name = args.name or f"day-{day:02d}"
    path = os.path.join(db.DEVOPS_HOME, "days", name, "exam.json")
    if not os.path.exists(path):
        print(c(f"\n  ℹ️  '{name}' uchun imtihon hali yo'q.\n", "yellow"))
        con.close(); return
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    tasks = data["tasks"]
    maxpts = sum(t["points"] for t in tasks)
    passpct = data.get("pass_score", 70)
    limit = data.get("time_limit_min", 15)
    rel_ws = data.get("workspace", f"days/{name}/exam")
    workspace = os.path.join(db.DEVOPS_HOME, rel_ws)
    os.makedirs(workspace, exist_ok=True)

    print(c(f"\n  ╔═══════ 🎓 IMTIHON — {data.get('title', name)} ═══════╗", "mag"))
    print(c("  ⚠️  Bu QUIZ EMAS — AMALIY imtihon. Hint YO'Q. Qattiq nazorat.", "red"))
    print(f"  📋 {len(tasks)} topshiriq  ·  ⏱️ {limit} daqiqa  ·  ✅ o'tish: {passpct}%")
    print(f"  📂 Ish papkang:  {c('~/devops/' + rel_ws, 'cyan')}")
    print(c("  Har topshiriqni terminalда bajar, keyin Enter bos — men tekshiraman.", "dim"))
    try:
        input(c("\n  Tayyormisan? Boshlash uchun Enter (yoki Ctrl+C bekor)... ", "yellow"))
    except (EOFError, KeyboardInterrupt):
        print(); con.close(); return

    start = time.time()
    score = 0
    for i, t in enumerate(tasks, 1):
        if (time.time() - start) / 60 > limit:
            print(c("\n  ⏰ VAQT TUGADI! Qolgan topshiriqlar yopildi.", "red"))
            break
        remaining = max(0, limit - (time.time() - start) / 60)
        print(c(f"\n  ─── Topshiriq {i}/{len(tasks)}  (⏱️ {remaining:.0f} daq · {t['points']} ball) ───", "bold"))
        print(f"  {t['prompt']}")
        while True:
            try:
                cmd = input(c("  [Enter=tekshir · s=skip · q=tugat]: ", "yellow")).strip().lower()
            except (EOFError, KeyboardInterrupt):
                cmd = "q"
            if cmd == "q":
                print(c("  ⏹️ Imtihon tugatildi.", "yellow"))
                _exam_finish(con, name, score, maxpts, passpct)
                con.close(); return
            if cmd == "s":
                print(c("  ⏭️ Tashlab ketildi (0 ball).", "dim"))
                break
            if (time.time() - start) / 60 > limit:
                print(c("  ⏰ Vaqt tugadi!", "red"))
                break
            if _exam_check(t["check"], workspace):
                print(c(f"  ✅ TO'G'RI! +{t['points']} ball", "green"))
                score += t["points"]
                break
            print(c("  ❌ Noto'g'ri. Qayta urin (hint yo'q, o'zing top).", "red"))
    _exam_finish(con, name, score, maxpts, passpct)
    con.close()


# ═══════════════ AI MENTOR funksiyalari (markaziy, robust) ═══════════════

def ai_ask(system, prompt, max_tokens=700):
    """Markaziy AI chaqiruv — xatolarni chiroyli boshqaradi. Matn yoki None qaytaradi."""
    key = load_key()
    if not key:
        print(c("  ⚠️  AI uchun API key kerak (engine/config.json).", "yellow"))
        return None
    try:
        return call_api(key, AI_MODEL, prompt, system=system, max_tokens=max_tokens).strip()
    except Exception as e:
        print(c(f"  ⚠️  AI javob bera olmadi: {e}", "yellow"))
        return None


def learner_context(con):
    """Boy bilim profili (learner model) — AI har muloqotда shuni o'qiydi."""
    try:
        return learner.ai_text(con)
    except Exception:
        return f"O'quvchi Day {current_day(con)}/56 da."


RANKS = [
    (0, "🐧 Tux Cadet"), (600, "🔧 Shell Apprentice"), (1400, "📦 Container Wrangler"),
    (2200, "🚀 Pipeline Pilot"), (3200, "☸️ Cluster Captain"), (4200, "🏗️ Infra Architect"),
    (5200, "📡 Observability Oracle"), (6000, "🎖️ Junior DevOps Engineer"),
]


def compute_xp(con):
    xp = 0
    cache = {}
    for r in con.execute("SELECT day, task_id FROM task_progress").fetchall():
        d = r["day"]
        if d not in cache:
            data = load_tasks(d) or {"tasks": []}
            cache[d] = {t["id"]: t.get("xp", 0) for t in data.get("tasks", [])}
        xp += cache[d].get(r["task_id"], 0)
    for r in con.execute("SELECT score FROM exam_results WHERE passed=1").fetchall():
        xp += r["score"] or 0
    xp += (con.execute("SELECT SUM(correct) FROM attempts").fetchone()[0] or 0) * 2
    return xp


def cmd_rank(args):
    """XP, daraja (rank), keyingi darajagacha progress va yutuqlar."""
    con = db.connect()
    xp = compute_xp(con)
    cur, nxt = RANKS[0], None
    for i, (th, name) in enumerate(RANKS):
        if xp >= th:
            cur = (th, name)
            nxt = RANKS[i + 1] if i + 1 < len(RANKS) else None
    print(c(f"\n  🎖️  DARAJA: {cur[1]}", "bold"))
    print(f"  ⭐ XP: {c(xp, 'cyan')}")
    if nxt:
        done, span = xp - cur[0], nxt[0] - cur[0]
        filled = int(20 * done / max(span, 1))
        print(f"  [{'█'*filled}{'░'*(20-filled)}]  {nxt[0]-xp} XP → {nxt[1]}")
    else:
        print(c("  🏆 Eng yuqori daraja — JUNIOR DEVOPS ENGINEER!", "green"))
    tp = con.execute("SELECT COUNT(*) FROM task_progress").fetchone()[0]
    bosses = con.execute("SELECT COUNT(*) FROM task_progress WHERE task_id='boss'").fetchone()[0]
    exams = con.execute("SELECT COUNT(*) FROM exam_results WHERE passed=1").fetchone()[0]
    nans = con.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
    ach = [("🩸 First Blood (1-topshiriq)", tp >= 1), ("🏴 Flag Hunter (boss flag)", bosses >= 1),
           ("🎓 Exam Master (imtihon o'tdi)", exams >= 1), ("📚 Quiz 50+", nans >= 50),
           ("🔥 Quiz 200+", nans >= 200)]
    print(c("\n  🏅 Yutuqlar:", "bold"))
    for name, got in ach:
        print(f"   {c('✅', 'green') if got else '⬜'} {name}")
    print()
    con.close()


def cmd_interview(args):
    """AI mock-intervyu: savol beradi, javobingni baholaydi."""
    n = args.n or 3
    qsys = ("You are a DevOps job interviewer. Output ONE concise interview question in "
            "Uzbek (English terms), junior level, on the given areas. ONLY the question.")
    esys = ("You are a DevOps interviewer evaluating an answer. Given QUESTION and ANSWER "
            "(Uzbek), reply in Uzbek: start with 'Baho: X/10', then 'Yaxshi:' (to'g'ri "
            "joylari), 'Yetishmadi:' (kamchilik), 'Ideal javob:' (qisqa namuna). Fair, "
            "encouraging.")
    areas = "Linux, ruxsatlar, jarayonlar/systemd, networking, docker, git"
    print(c(f"\n  🎤 MOCK INTERVYU ({n} savol) — javob ber, AI baholaydi. ('q'=chiqish)", "mag"))
    total = asked = 0
    for i in range(n):
        q = ai_ask(qsys, f"Sohalar: {areas}. {i+1}-savol (oldingilardan farqli).", max_tokens=200)
        if not q:
            break
        print(c(f"\n  ❓ Savol {i+1}: ", "bold") + q.strip())
        try:
            ans = input(c("  Javobing: ", "yellow")).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if ans.lower() in ("q", "quit", ""):
            break
        ev = ai_ask(esys, f"QUESTION: {q}\nANSWER: {ans}", max_tokens=600)
        if ev:
            print(c("  🧑‍⚖️ ", "cyan") + ev.replace("\n", "\n  "))
            asked += 1
            m = re.search(r"Baho:\s*(\d+)", ev)
            if m:
                total += int(m.group(1))
    if asked:
        print(c(f"\n  📊 Intervyu yakuni: o'rtacha {total/asked:.1f}/10 ({asked} savol)\n", "bold"))
    else:
        print()


def cmd_doctor(args):
    """Tizim salomatligini to'liq tekshiradi (self-check)."""
    print(c("\n  🩺 TIZIM SALOMATLIGI (doctor)\n", "bold"))
    results = []

    def add(name, ok, detail=""):
        results.append(ok)
        mark = c("✅", "green") if ok else c("❌", "red")
        print(f"   {mark} {name}" + (f"  {c(detail, 'dim')}" if detail else ""))

    con = db.connect()
    qn = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    add("Savol banki", qn > 0, f"{qn} savol")
    add("Holat (current_day)", db.get_meta(con, "current_day") is not None,
        f"Day {db.get_meta(con, 'current_day', '?')}")
    con.close()
    add("API key", bool(load_key()))
    for fn in ("cli.py", "db.py", "generate.py", "coach.py", "quizplan.py", "srs.py", "worklog.py"):
        add(f"engine/{fn}", os.path.exists(os.path.join(db.ENGINE_DIR, fn)))
    add("Telegram config", os.path.exists(
        os.path.join(db.DEVOPS_HOME, "scripts", "telegram", "config.json")))
    try:
        svc = subprocess.run(["systemctl", "is-active", "devops-quizbot"],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        add("Quizbot servis", svc == "active", svc)
    except Exception:
        add("Quizbot servis", False)
    try:
        cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5).stdout
        add("Cron eslatmalar", "devops-bootcamp" in cron)
    except Exception:
        add("Cron eslatmalar", False)
    for d in ("01", "02", "03"):
        add(f"Day-{d} fayllari", all(os.path.exists(os.path.join(
            db.DEVOPS_HOME, "days", f"day-{d}", x)) for x in ("MISSION.md", "tasks.json")))
    okc, tot = sum(results), len(results)
    color = "green" if okc == tot else "yellow"
    print(c(f"\n  Natija: {okc}/{tot} sog'lom", color))
    print(c("  ✅ Tizim to'liq sog'lom!\n" if okc == tot
            else "  ⚠️ Ba'zi joylar e'tibor talab qiladi.\n", color))


def cmd_roadmap(args):
    """Butun 56 kunlik yo'l xaritasi — qayerdasan, oldinda nima bor."""
    con = db.connect()
    cur = current_day(con)
    done = {r["day"] for r in con.execute("SELECT day FROM day_progress WHERE status='done'")}
    con.close()
    try:
        weeks = json.load(open(os.path.join(db.ENGINE_DIR, "roadmap.json"), encoding="utf-8"))
    except Exception:
        print(c("\n  ⚠️ roadmap.json topilmadi.\n", "yellow"))
        return
    total = sum(len(w["days"]) for w in weeks)
    print(c(f"\n  🗺️  BUTUN YO'L — {total} kun / {len(weeks)} hafta", "bold"))
    print(c(f"  📍 Hozir: Day {cur}   ·   ✅ Tugatilgan: {len(done)}/{total}\n", "dim"))
    for w in weeks:
        wdays = [d["day"] for d in w["days"]]
        col = "green" if all(d in done for d in wdays) else ("mag" if cur in wdays else "cyan")
        print(c(f"  ─── {w['n']}-HAFTA: {w['theme']} ───", col))
        for d in w["days"]:
            if d["day"] in done:
                mark = c("✅", "green")
            elif d["day"] == cur:
                mark = c("📍", "yellow")
            else:
                mark = "⬜"
            line = f"   {mark} Day {d['day']:02d} — {d['title']}"
            print(c(line + "   ← SEN SHU YERDASAN", "yellow") if d["day"] == cur else line)
    print(c("\n  Har kun: devops today → start → task/lab/quiz → done\n", "dim"))


def cmd_focus(args):
    """🧠 AI sening zaif mavzularingга qarab shaxsiy amaliy topshiriq beradi."""
    con = db.connect()
    day = current_day(con)
    rows = con.execute(
        "SELECT q.topic, COUNT(*) n, SUM(a.correct) ok FROM attempts a "
        "JOIN questions q ON q.id=a.question_id GROUP BY q.topic").fetchall()
    con.close()
    ranked = sorted((100 * (r["ok"] or 0) // r["n"], r["topic"]) for r in rows if r["n"] >= 2)
    weak = [t for p, t in ranked if p < 70][:3]
    focus = ", ".join(weak) if weak else "umumiy DevOps asoslari"
    sysp = ("You are 'Ustoz'. Create ONE focused, practical hands-on mini-assignment in Uzbek "
            "(English terms/commands) for the learner's WEAK area(s). Real-world, not a toy. "
            "Structure with headers: 🎯 Vazifa (aniq, real kontekst); 📋 Qadamlar (raqamli); "
            "✅ O'zingni qanday tekshirasan. Keep it tight and doable in ~15-20 min.")
    print(c(f"\n  🧠 AI sen uchun topshiriq tayyorlayapti  (zaif: {focus})...", "dim"))
    ans = ai_ask(sysp, f"O'quvchi Day {day}/56. Eng zaif mavzular: {focus}. "
                 "Shu mavzu(lar)ga 1 ta amaliy, tekshiriladigan topshiriq ber.", max_tokens=900)
    if ans:
        print(c("\n  🎯 SHAXSIY TOPSHIRIQ (zaif joyingга):", "bold"))
        print("  " + ans.replace("\n", "\n  ") + "\n")


def _recent_cmds(n=15):
    import datetime as _dt
    logf = os.path.join(db.DEVOPS_HOME, "logs", "activity",
                        f"commands-{_dt.date.today().isoformat()}.log")
    cmds = []
    if os.path.exists(logf):
        with open(logf) as f:
            for ln in f.readlines()[-n:]:
                parts = ln.split("|", 3)
                if len(parts) == 4:
                    cmds.append(parts[3].strip())
    return cmds


def _current_task_ctx(con):
    day = current_day(con)
    data = load_tasks(day)
    if not data:
        return f"O'quvchi Day {day}/56 da."
    done = db.done_task_ids(con, day)
    pend = [t for t in data["tasks"] if t["id"] not in done]
    if not pend:
        return f"O'quvchi Day {day}/56 da — barcha topshiriq bajarilgan."
    t = pend[0]
    return (f"O'quvchi Day {day}/56 da. Hozirgi topshirig'i: \"{t['title']}\" — {t.get('why','')} "
            f"Qadamlar: {t.get('steps','')} Kutilgan: {t.get('expect','')}")


def cmd_ai(args):
    """🤖 AI: loglar + joriy topshiriq + savolni BIRGA ko'rib javob beradi."""
    if not load_key():
        print(c("\n  ⚠️  AI uchun API key kerak (engine/config.json).\n", "yellow")); return
    q = " ".join(args.text).strip() if getattr(args, "text", None) else ""
    con = db.connect()
    ctx = learner_context(con)
    task_ctx = _current_task_ctx(con)
    con.close()
    cmds = _recent_cmds()
    cmds_txt = ("\nOxirgi terminal buyruqlari:\n" + "\n".join(f"- {x}" for x in cmds)) if cmds else ""

    if q:                                    # savol berildi -> loglar+topshiriq bilan javob
        sysp = ("You are 'Ustoz', a DevOps mentor sitting next to the learner. You CAN SEE their "
                "recent terminal commands and current task — USE them. If they ask why something "
                "isn't working, find the real cause IN their recent commands (e.g. wrong path, "
                "wrong flag). Do NOT ask for info you can already see. Answer in Uzbek (English "
                "terms/commands), concrete and short, with a fixed command example when relevant.")
        print(c("\n  🤔 Ustoz loglar + savolingni o'qiyapti...", "dim"))
        ans = ai_ask(sysp, f"{ctx}\n{task_ctx}{cmds_txt}\n\nSavol: {q}", max_tokens=900)
        if ans:
            print(c("\n  🧑‍🏫 USTOZ:", "bold"))
            print("  " + ans.replace("\n", "\n  ") + "\n")
        return

    if not cmds:                             # savol yo'q, log ham yo'q
        print(c("\n  💡 Foydalanish:  devops ai \"savol\"   (yoki ishlab tur, keyin devops ai)\n", "yellow")); return
    print(c("\n  🤔 Ustoz loglaringni o'qiyapti...", "dim"))
    txt = ai_ask(AI_HELP_SYSTEM, f"{ctx}\n{task_ctx}{cmds_txt}\n\nNima qilyapti? Qisqa yordam ber.",
                 max_tokens=400)
    if txt:
        print(c("\n  🤖 USTOZ-AI:", "bold"))
        print("  " + txt.replace("\n", "\n  ") + "\n")


def ensure_ready(con):
    """devops init kerak emas: bank bo'sh bo'lsa, seed'larni avtomatik import qiladi."""
    if con.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        for s in (os.path.join(db.ENGINE_DIR, "seed"),
                  os.path.join(db.DEVOPS_HOME, "scripts", "telegram", "quizbank")):
            db.import_seed_dir(con, s)


def print_help_uz():
    print(c("\n  🐧 devops — DevOps Bootcamp boshqaruv markazi\n", "bold"))
    rows = [
        ("roadmap", "🗺️ Butun 56 kunlik yo'l — qayerdasan, oldinda nima bor"),
        ("today", "Bugun nima qilaman? (kun, vaqt, muhlat, ish)  ⭐ shu yerdan boshla"),
        ("next", "👉 Keyingi ishni aniq ko'rsatadi  ⭐ kunlik oqim"),
        ("verify", "🧠 Topshirig'ingni tekshiradi (AI/flag) → keyingisiga o'tasan"),
        ("task", "Barcha topshiriqlar ro'yxati  ·  task <N> = batafsil"),
        ("focus", "🧠 AI zaif mavzuingga moslangan shaxsiy topshiriq beradi"),
        ("quiz", "Cheksiz quiz  ·  quiz today = bugungi mavzu  ·  quiz docker = mavzu"),
        ("review", "SRS takror — eski mavzularni mustahkamlash (unutmaslik)"),
        ("exam", "🎓 Amaliy imtihon — hintsiz, qattiq nazorat, real tekshiruv"),
        ("ai", "🤖 AI: ai \"savol/mavzu\" (tushuntir·shpargalka·javob) yoki bo'sh = loglardan"),
        ("interview", "🤖 AI mock-intervyu — savol beradi, javobingni baholaydi"),
        ("rank", "🎖️ Daraja, XP, progress va yutuqlar"),
        ("profile", "Men haqimda: kuchli/zaif mavzular, aniqlik, progress"),
        ("deadline", "Muhlat va bugun ishlangan vaqt"),
        ("doctor", "🩺 Tizim salomatligini tekshirish"),
        ("stats", "Savollar banki statistikasi"),
    ]
    for cmd, desc in rows:
        left = "devops " + cmd
        print("  " + c(left, "cyan") + " " * max(2, 20 - len(left)) + "  " + desc)
    print(c("\n  🔁 KUNLIK OQIM:  devops next  →  (ishni bajar)  →  devops verify   (kun avtomatik yakunlanadi)", "green"))
    print(c("  Quiz ichida:  a/b/c/d = javob  ·  ? = AI yordam  ·  q = chiqish\n", "dim"))


def main():
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help", "help"):
        print_help_uz()
        return

    p = argparse.ArgumentParser(prog="devops", description="DevOps Bootcamp runner")
    sub = p.add_subparsers(dest="cmd")
    pq = sub.add_parser("quiz"); pq.add_argument("topic", nargs="?"); pq.add_argument("-n", type=int, default=0, help="nechta savol (0 = cheksiz oqim, default)")
    pr = sub.add_parser("review"); pr.add_argument("-n", type=int, default=15)
    pcp = sub.add_parser("checkpoint"); pcp.add_argument("topic", nargs="?")
    sub.add_parser("stats")
    sub.add_parser("today")
    sub.add_parser("deadline")
    sub.add_parser("profile")
    pai = sub.add_parser("ai"); pai.add_argument("text", nargs="*")
    pe = sub.add_parser("exam"); pe.add_argument("name", nargs="?")
    piv = sub.add_parser("interview"); piv.add_argument("-n", type=int, default=3)
    sub.add_parser("rank")
    sub.add_parser("doctor")
    sub.add_parser("roadmap")
    sub.add_parser("focus")
    sub.add_parser("next")
    pvf = sub.add_parser("verify"); pvf.add_argument("n", nargs="?")
    pt = sub.add_parser("task")
    pt.add_argument("a", nargs="?")
    pt.add_argument("b", nargs="?")
    args = p.parse_args()

    db.init()                                  # sxema (idempotent)
    _con = db.connect(); ensure_ready(_con)                 # init kerak emas — avto seed
    try:
        ensure_work(current_day(_con))                      # ish joyi har doim tayyor
    except Exception:
        pass
    _con.close()

    dispatch = {
        "quiz": cmd_quiz, "review": cmd_review, "checkpoint": cmd_checkpoint, "stats": cmd_stats,
        "today": cmd_today, "task": cmd_task, "deadline": cmd_deadline,
        "profile": cmd_profile, "ai": cmd_ai, "exam": cmd_exam,
        "interview": cmd_interview, "rank": cmd_rank, "doctor": cmd_doctor,
        "roadmap": cmd_roadmap, "focus": cmd_focus, "next": cmd_next, "verify": cmd_verify,
    }
    try:                                       # robustlik: xato bo'lsa ham chiroyli
        if args.cmd in dispatch:
            dispatch[args.cmd](args)
        else:
            print_help_uz()
    except KeyboardInterrupt:
        print(c("\n  ⏹️ Bekor qilindi.\n", "yellow"))
    except Exception as e:
        print(c(f"\n  ⚠️ Xato yuz berdi: {e}\n  (Agar takrorlansa, devops doctor bilan tekshir.)\n", "red"))


if __name__ == "__main__":
    main()
