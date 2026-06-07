#!/usr/bin/env python3
"""
DevOps Bootcamp — Telegram xabarnoma skripti.
Tashqi kutubxona kerak emas (faqat Python standart kutubxonasi).

Token va chat_id ni quyidagilardan oladi (shu tartibda):
  1. Muhit o'zgaruvchilari: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
  2. config.json fayli (shu papkada): {"token": "...", "chat_id": "..."}

Foydalanish:
  python3 notify.py "Salom dunyo"          # xabar yuborish
  python3 notify.py --get-chat-id          # chat_id ni topish
  python3 notify.py --test                 # ulanishni tekshirish
  echo "matn" | python3 notify.py -        # stdin'dan xabar
"""
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
API = "https://api.telegram.org/bot{token}/{method}"


def load_creds():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if (not token or not chat_id) and os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        token = token or cfg.get("token")
        chat_id = chat_id or cfg.get("chat_id")
    return token, chat_id


def api_call(token, method, params):
    url = API.format(token=token, method=method)
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=15) as r:
        return json.load(r)


def send(token, chat_id, text):
    res = api_call(token, "sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    })
    if not res.get("ok"):
        print("❌ Xato:", res, file=sys.stderr)
        sys.exit(1)
    print("✅ Xabar yuborildi.")


def get_chat_id(token):
    res = api_call(token, "getUpdates", {})
    if not res.get("ok"):
        print("❌ Xato:", res, file=sys.stderr)
        sys.exit(1)
    updates = res.get("result", [])
    if not updates:
        print("⚠️  Hali hech qanday xabar yo'q.")
        print("   Telegram'da botingga /start yoki biror xabar yubor, keyin qayta ishga tushir.")
        return
    seen = {}
    for u in updates:
        msg = u.get("message") or u.get("channel_post") or {}
        chat = msg.get("chat", {})
        if chat.get("id"):
            seen[chat["id"]] = chat.get("username") or chat.get("title") or chat.get("first_name", "?")
    print("📋 Topilgan chat'lar:")
    for cid, name in seen.items():
        print(f"   chat_id = {cid}   ({name})")
    print("\n👉 Yuqoridagi chat_id ni config.json ga yoz (yoki ustozga ayt).")


def main():
    args = sys.argv[1:]
    token, chat_id = load_creds()

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN topilmadi. SETUP.md ni o'qi.", file=sys.stderr)
        sys.exit(2)

    if not args:
        print(__doc__)
        sys.exit(0)

    if args[0] == "--get-chat-id":
        get_chat_id(token)
        return

    if args[0] == "--test":
        if not chat_id:
            print("❌ chat_id yo'q. Avval --get-chat-id bilan top.", file=sys.stderr)
            sys.exit(2)
        send(token, chat_id, "🐧 <b>DevOps Bootcamp</b>\nTelegram ulandi! Tayyormiz, agent. 🚀")
        return

    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID topilmadi. SETUP.md ni o'qi.", file=sys.stderr)
        sys.exit(2)

    text = sys.stdin.read() if args[0] == "-" else " ".join(args)
    send(token, chat_id, text)


if __name__ == "__main__":
    main()
