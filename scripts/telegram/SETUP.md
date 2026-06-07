# 🤖 Telegram Bot — Ulash Yo'riqnomasi

3 daqiqalik ish. Telefoningda Telegram'ni och va boshla.

## 1-qadam: Bot yarat (@BotFather)
1. Telegram'da **@BotFather** ni qidirib top va `/start` bos.
2. `/newbot` yoz.
3. Botga **nom** ber (masalan: `DevOps Ustoz`).
4. **Username** ber — `bot` bilan tugashi shart (masalan: `my_devops_ustoz_bot`).
5. BotFather senga **TOKEN** beradi, shu ko'rinishda:
   ```
   7123456789:AAH...juda-uzun-maxfiy-kalit...xyz
   ```
   ⚠️ Bu tokenni hech kimga berma — bu botning paroli.

## 2-qadam: Botga "salom" de
- Yangi botingni qidirib top (yuqoridagi username bilan) va **`/start`** bos
  (yoki istalgan xabar yoz). Bu kerak — bot sen bilan gaplashishi uchun
  avval SEN unga yozishing shart.

## 3-qadam: Tokenni ustozga ber
Tokenni shu chatда menga (Claude) yubor. Men:
- `config.json` ga xavfsiz yozaman (ruxsatlarni 600 qilaman),
- `chat_id` ingni avtomatik aniqlayman,
- test xabar yuboraman.

> Token oqib ketmasligi uchun `config.json` git'ga **qo'shilmaydi** (`.gitignore` da).

---

## Qo'lda tekshirish (xohlasang)
```bash
cd ~/devops/scripts/telegram
# token va chat_id config.json da bo'lsa:
python3 notify.py --test
python3 notify.py "Bu mening birinchi botim xabari 🚀"
```

## config.json formati
```json
{
  "token": "7123456789:AAH...",
  "chat_id": "123456789"
}
```
