#!/usr/bin/env python3
"""Ob-havo (Samarqand) — Telegram. wttr.in (tekin, key yo'q). Ertalab cron yuboradi."""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from notify import load_creds, send  # noqa: E402

URL = "https://wttr.in/Samarkand?format=j1"

EMOJI = {
    "sun": "☀️", "clear": "🌙", "cloud": "☁️", "rain": "🌧️",
    "snow": "❄️", "fog": "🌫️", "thunder": "⛈️", "overcast": "☁️",
}


def pick_emoji(desc):
    d = desc.lower()
    for k, e in EMOJI.items():
        if k in d:
            return e
    return "🌤️"


def main():
    token, chat_id = load_creds()
    if not token:
        return
    try:
        with urllib.request.urlopen(URL, timeout=20) as r:
            data = json.load(r)
    except Exception as e:
        send(token, chat_id, f"⚠️ Ob-havo olinmadi: {e}")
        return
    cur = data["current_condition"][0]
    today = data["weather"][0]
    desc = cur["weatherDesc"][0]["value"]
    astro = today["astronomy"][0]
    msg = (
        f"{pick_emoji(desc)} <b>Ob-havo — Samarqand</b>\n\n"
        f"🌡️ Hozir: <b>{cur['temp_C']}°C</b> (his: {cur['FeelsLikeC']}°C)\n"
        f"📋 Holat: {desc}\n"
        f"📈 Bugun: {today['mintempC']}°…{today['maxtempC']}°C\n"
        f"💨 Shamol: {cur['windspeedKmph']} km/soat\n"
        f"💧 Namlik: {cur['humidity']}%\n"
        f"🌅 Quyosh: {astro['sunrise']}  ·  🌇 {astro['sunset']}\n\n"
        f"Xayrli tong, agent! Bugun ham zo'r kun bo'ladi. 💪"
    )
    send(token, chat_id, msg)


if __name__ == "__main__":
    main()
