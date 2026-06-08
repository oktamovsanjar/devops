# Day-09 — Cron & maintenance (to'liq kun)

### 🎯 Bugungi maqsad
Ishlarni **rejalashtirib** avtomatlashtirish: `cron`, backup skriptlari, eski
fayllarni tozalash (log rotation). Server o'zini o'zi parvarish qilsin.

> 📦 **Natija:** sana bilan nomlangan backup yaratuvchi skript + uni har kuni
> ishga tushiradigan cron yozuvi.

> ⚠️ **Xavfsizlik:** bu kun cron yozuvlarini FAYLGA yozasan (jonli crontab'ingga
> tegmaymiz — unда prayer/quiz ishlari bor).

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (crontab -l, sana formati) · 2️⃣ Drill (cron sintaksisi) ·
3️⃣ Asosiy (backup skript, cron yozuv, tozalash) · 4️⃣ Callback (Day-8 robust, Day-3 ps) ·
5️⃣ Mini-loyiha "Backup & Maintenance" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Cron — 5 ta vaqt maydoni
```
┌─ daqiqa (0-59)
│ ┌─ soat (0-23)
│ │ ┌─ oyning kuni (1-31)
│ │ │ ┌─ oy (1-12)
│ │ │ │ ┌─ hafta kuni (0-7, 0/7=yakshanba)
│ │ │ │ │
* * * * *  buyruq
```
| Yozuv | Ma'no |
|-------|-------|
| `* * * * *` | har daqiqa |
| `0 3 * * *` | har kuni 03:00 |
| `0 9 * * 1` | har dushanba 09:00 |
| `*/5 * * * *` | har 5 daqiqada |

Tahrirlash:  `crontab -e`  ·  Ko'rish:  `crontab -l`

### 2. Backup — sana bilan nomlash
```
dest="backup-$(date +%F)"      # backup-2026-06-09
mkdir -p "$dest" && cp -r src/* "$dest"/
```

### 3. Eski fayllarni tozalash (log rotation)
```
find /var/log -name "*.log" -mtime +7 -delete   # 7 kundan eski .log larni o'chir
```

### 4. Maintenance log
```
echo "$(date) backup bajarildi" >> /var/log/backup.log
```

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
