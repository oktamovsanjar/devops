# Day-07 — 1-hafta BOSS

### 🎯 Bugungi maqsad
1-haftaning **yakuniy sinovi**: butun hafta o'rganganingni (navigatsiya, ruxsat,
jarayon, matn, tarmoq, bash) bitta **real loyihada** birlashtirasan — server
**Health-Check** vositasi.

> 📦 **Natija:** ishlaydigan monitoring skripti + log tahlili = mini-loyiha.

---

## 📚 Bu hafta nimani o'rganding (qisqa takror)

| Day | Mavzu | Asosiy |
|-----|-------|--------|
| 1 | Navigatsiya | `ls`, `cd`, `find`, `grep`, `>` |
| 2 | Ruxsatlar | `chmod`, `chown`, `sudo` |
| 3 | Jarayonlar | `ps`, `kill`, `systemctl`, `journalctl` |
| 4 | Matn | `grep`, `sed`, `awk`, `\|` |
| 5 | Tarmoq | `ip`, `ss`, `dns`, `curl` |
| 6 | Bash | o'zgaruvchi, if, for, funksiya |

Bugun shularning hammasini ishlatasan.

---

## 🏗️ Bugungi loyiha: Health-Check
Server holatini ko'rsatuvchi vosita quramiz:
- `health/bin/check.sh` — hostname, CPU, disk holatini chiqaradi (bash)
- `health/logs/errors.txt` — logдан ERROR soni (grep)
- `health/logs/report.txt` — skript natijasi (saqlangan)

Har qadam — bir haftalik ko'nikmaning amaliyoti.

---

## ▶️ Endi ishga
```
devops next       # nima qilishni aytadi
devops verify     # tekshiradi → keyingisi
```
Hammasi tugasa — **1-hafta yakunlanadi**, Day-8 (Bash II) ochiladi! 🎉
