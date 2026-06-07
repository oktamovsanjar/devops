#!/usr/bin/env python3
"""
Namoz vaqtlari (Samarqand) — Telegram eslatma. Aladhan API (tekin, key yo'q).

  python3 prayer.py --daily    # bugungi 5 vaqtni Telegram'ga yuborish + cache
  python3 prayer.py --check    # cron (har 5 daq): vaqti kelgan namozni eslatish
"""
import datetime
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from notify import load_creds, send  # noqa: E402

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Samarkand")
except Exception:
    TZ = None

CACHE = os.path.join(HERE, "prayer-times.json")
# method=3 (Muslim World League), school=1 (Hanafi) — O'rta Osiyoga mos. Kerak bo'lsa o'zgartiramiz.
URL = ("https://api.aladhan.com/v1/timingsByCity?city=Samarkand&country=Uzbekistan"
       "&method=3&school=1")
PRAYERS = [("Fajr", "Bomdod 🌅"), ("Dhuhr", "Peshin ☀️"), ("Asr", "Asr 🌇"),
           ("Maghrib", "Shom 🌆"), ("Isha", "Xufton 🌙")]


def today():
    return (datetime.datetime.now(TZ) if TZ else datetime.datetime.now()).strftime("%Y-%m-%d")


def now_min():
    n = datetime.datetime.now(TZ) if TZ else datetime.datetime.now()
    return n.hour * 60 + n.minute


def fetch():
    with urllib.request.urlopen(URL, timeout=15) as r:
        data = json.load(r)
    t = data["data"]["timings"]
    return {k: t[k][:5] for k in [p[0] for p in PRAYERS]}


def get_times():
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            c = json.load(f)
        if c.get("date") == today():
            return c["timings"]
    timings = fetch()
    with open(CACHE, "w") as f:
        json.dump({"date": today(), "timings": timings}, f)
    return timings


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--daily"
    token, chat_id = load_creds()
    if not token:
        return
    timings = get_times()

    if mode == "--daily":
        lines = ["🕌 <b>Bugungi namoz vaqtlari — Samarqand</b>", ""]
        for key, uz in PRAYERS:
            lines.append(f"  {uz}: <b>{timings[key]}</b>")
        lines.append("\nAlloh qabul qilsin. 🤲")
        send(token, chat_id, "\n".join(lines))

    elif mode == "--check":
        notified_file = os.path.join(HERE, "..", "..", "logs", f"prayer-notified-{today()}.txt")
        done = set()
        if os.path.exists(notified_file):
            with open(notified_file) as f:
                done = set(f.read().split())
        nm = now_min()
        for key, uz in PRAYERS:
            hh, mm = map(int, timings[key].split(":"))
            pm = hh * 60 + mm
            if 0 <= nm - pm <= 5 and key not in done:
                send(token, chat_id, f"🕌 <b>{uz} namozi vaqti kirdi</b> ({timings[key]}).\nAllohu akbar 🤲")
                done.add(key)
        os.makedirs(os.path.dirname(notified_file), exist_ok=True)
        with open(notified_file, "w") as f:
            f.write(" ".join(done))


if __name__ == "__main__":
    main()
