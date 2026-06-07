#!/usr/bin/env python3
"""
DevOps Bootcamp — Kunlik faoliyat hisoboti.
Terminal activity log'idan kun davomidagi mehnatni hisoblaydi.

Foydalanish:
  python3 day-report.py                 # bugungi hisobot (ekranga)
  python3 day-report.py 2026-06-04      # belgilangan sana
  python3 day-report.py --telegram      # bugungi hisobotni Telegram'ga yuborish
"""
import os
import sys
import subprocess
from collections import Counter
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DEVOPS_HOME = os.environ.get("DEVOPS_HOME", os.path.expanduser("~/devops"))
LOG_DIR = os.path.join(DEVOPS_HOME, "logs", "activity")
IDLE_GAP_MIN = 10          # 10 daqiqadan katta tanaffus "ish" sanalmaydi
NOISE = {"ls", "cd", "pwd", "clear", "ll", "la", "cat", "history"}


def parse(date):
    path = os.path.join(LOG_DIR, f"commands-{date}.log")
    if not os.path.exists(path):
        return None, path
    rows = []
    with open(path) as f:
        for line in f:
            parts = [p.strip() for p in line.split("|", 3)]
            if len(parts) != 4:
                continue
            ts, ec, cwd, cmd = parts
            try:
                t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            ec = ec.replace("ec=", "")
            rows.append((t, ec, cwd, cmd))
    return rows, path


def active_minutes(times):
    if len(times) < 2:
        return 0.0
    total = 0.0
    for a, b in zip(times, times[1:]):
        gap = (b - a).total_seconds() / 60.0
        if gap <= IDLE_GAP_MIN:
            total += gap
    return total


def build_report(date):
    rows, path = parse(date)
    if not rows:
        return f"📭 {date} uchun faoliyat log'i topilmadi.\n({path})\nTerminalда biror buyruq tergan bo'lsang shu yerga yoziladi."

    times = [r[0] for r in rows]
    first, last = times[0], times[-1]
    total = len(rows)
    errors = sum(1 for r in rows if r[1] not in ("0", ""))
    active = active_minutes(times)
    span = (last - first).total_seconds() / 60.0

    first_words = [r[3].split()[0] for r in rows if r[3].split()]
    top = Counter(first_words).most_common(8)
    learned = Counter(w for w in first_words if w not in NOISE).most_common(6)

    h_active, m_active = divmod(int(active), 60)
    h_span, m_span = divmod(int(span), 60)

    lines = [
        f"📊 <b>Kunlik hisobot — {date}</b>",
        "",
        f"⏱️  Faol vaqt: <b>{h_active}s {m_active}d</b>  (oraliq: {h_span}s {m_span}d)",
        f"🖥️  Buyruqlar: <b>{total}</b>   ·   ❌ Xatolar: {errors}  ({100*errors//max(total,1)}%)",
        f"🟢 Birinchi: {first.strftime('%H:%M')}   🔴 Oxirgi: {last.strftime('%H:%M')}",
        "",
        "🔧 <b>Eng ko'p ishlatilgan buyruqlar:</b>",
    ]
    for cmd, n in top:
        lines.append(f"   {cmd:<12} ×{n}")
    if learned:
        lines.append("")
        lines.append("📚 <b>Bugungi \"yangi qurollar\" (shovqinsiz):</b>")
        lines.append("   " + ", ".join(f"{c}×{n}" for c, n in learned))
    lines.append("")
    lines.append("💪 Ajoyib mehnat, agent. Streak'ni uzma!")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    to_tg = "--telegram" in args
    args = [a for a in args if a != "--telegram"]
    date = args[0] if args else datetime.now().strftime("%Y-%m-%d")

    report = build_report(date)

    if to_tg:
        notify = os.path.join(HERE, "..", "telegram", "notify.py")
        subprocess.run([sys.executable, notify, report], check=False)
    else:
        # ekranда HTML teglarni tozalab ko'rsatamiz
        print(report.replace("<b>", "").replace("</b>", ""))


if __name__ == "__main__":
    main()
