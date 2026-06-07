#!/usr/bin/env bash
# ============================================================
# DevOps Bootcamp — Telegram kunlik eslatmalar (cron chaqiradi)
# Foydalanish: cron-reminders.sh {morning|lunch|quiz|evening|streak}
# ============================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVOPS_HOME="${DEVOPS_HOME:-$HOME/devops}"
NOTIFY=(python3 "$HERE/notify.py")
REPORT=(python3 "$DEVOPS_HOME/scripts/monitoring/day-report.py")

DOW=$(date +%u)   # 1=Dush ... 7=Yakshanba

case "${1:-}" in
  morning)
    if [ "$DOW" = "7" ]; then
      "${NOTIFY[@]}" "🌴 <b>Yakshanba — DAM KUNI</b>
Bugun yangi narsa o'rganmaysan. Miya bilganini shu kuni mustahkamlaydi.
Eslatmalarni ko'r, papkani tartibla, dam ol. Ertaga yangi kuch bilan! 💪"
    else
      "${NOTIFY[@]}" "☀️ <b>Xayrli tong, agent!</b>
Yangi DevOps kuni boshlandi. 🎯

1️⃣ Kechagi ishni ko'r
2️⃣ Bugungi mission'ni och
3️⃣ Terminalда <b>ustozga</b> kunni boshlaganingni ayt

Standup vaqti — qani, ishga! 🚀"
    fi
    ;;
  lunch)
    "${NOTIFY[@]}" "🍽️ <b>Tushlik vaqti!</b>
Ekrandan uzoqlash — bu majburiy, dangasalik emas.
Ovqatlan, biroz yur, ko'zingni dam oldir. 20-30 daqiqa. ⏳
Charchagan miya o'rganmaydi. 🧠"
    ;;
  quiz)
    # Kuzatiladigan quiz oqimini boshlash (javob -> keyingisi avtomatik keladi)
    python3 - <<'PY'
import sys
sys.path.insert(0, "/home/ubuntu/devops/scripts/telegram")
sys.path.insert(0, "/home/ubuntu/devops/engine")
from notify import load_creds
import db, quizbot
from generate import load_key
t, c = load_creds()
con = db.connect(); db.set_meta(con, "tg_active", "1")
quizbot.send_quiz(t, c, con, load_key())
PY
    ;;
  evening)
    "${REPORT[@]}" --telegram
    "${NOTIFY[@]}" "🌙 <b>Kun yakuni — Retro</b>
Bugun:
• Nimani o'rgandim?
• Nima qiyin bo'ldi?
• Ertaga nimaga e'tibor beraman?

Ishingni <code>git commit</code> qilishni unutma! Ustozga <b>kun tugatdim</b> deb yoz. ✅"
    ;;
  streak)
    "${NOTIFY[@]}" "🔥 <b>Streak tekshiruvi (21:00)</b>
Bugun mission'ni yakunladingmi? PROGRESS'ni yangiladingmi?
Streak — bu eng kuchli super-kuching. Uzma! 💪
(Hali ulgurmagan bo'lsang, hozir 15 daqiqa ajrat.)"
    ;;
  *)
    echo "Foydalanish: $0 {morning|lunch|quiz|evening|streak}" >&2
    exit 1
    ;;
esac
