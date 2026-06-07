# 🎯 MISSION DAY-03 — "Jonli Tizim"
### Mavzu: Jarayonlar (processes), signallar, `systemd` servislar, `journald` loglar
### Rank: 🐧 Tux Cadet · Asosiy XP: 100 · Maksimal: ~450

---

## 🗺️ BRIEFING

Agent, server — bu jonli organizm. Unda **jarayonlar** (processes) yashaydi:
nginx, baza, sening botlaring. Bugun sen ularni **ko'rasan, boshqarasan, va
kerak bo'lsa qayta tiklaysan**.

> **Real kontekst (tunda telefon jiringladi):** "Sayt ishlamayapti!" SSH bilan
> kirding. Qaysi jarayon o'lgan? `systemctl status`. Nega o'lgan? `journalctl`.
> Qayta tikla: `systemctl restart`. **3 ta buyruq — muammo hal.** Mana shu —
> DevOps/SRE muhandisining non-yog'i. Bugun shuni o'rganasan.

---

## 📚 LEARN

### 1. Jarayonlar (processes)
Har ishlayotgan dastur — jarayon, o'z **PID** (Process ID) raqamiga ega.
```
ps aux              # BARCHA jarayonlar (a=all, u=batafsil, x=terminalsiz ham)
ps aux | grep nginx # nginx jarayonini top
top    (yoki htop)  # jonli, real-time (chiqish: q)
pgrep -f botname    # nom bo'yicha PID
```
Har jarayonning **ota-onasi (PPID)** bor — daraxt. PID 1 = `systemd` (hammaning ajdodi).

### 2. Signallar — jarayonlarga "xabar"
`kill` aslida "o'ldirish" emas, **signal yuborish**:
| Signal | Raqam | Ma'no |
|--------|-------|-------|
| SIGTERM | 15 | "Iltimos, chiroyli to'xta" (default) |
| SIGKILL | 9 | "Majburan o'l" (oxirgi chora, tozalanmaydi) |
| SIGHUP | 1 | "Konfigni qayta o'qi" |
| SIGINT | 2 | Ctrl+C (to'xtat) |
| SIGUSR1 | 10 | Dasturchi belgilagan maxsus ish |
```
kill 1234           # SIGTERM (yumshoq)
kill -9 1234        # SIGKILL (majburiy)
kill -USR1 1234     # maxsus signal
pkill -f botname    # nom bo'yicha
```
> 💡 Dasturlar signalni **"ushlashi" (trap)** mumkin — masalan SIGTERM kelganda
> ishini saqlab, keyin to'xtash. Bugungi boss aynan shuni ishlatadi (SIGUSR1).

### 3. Fonda ishlatish (background jobs)
```
./uzun_ish.sh &     # & = orqa fonda ishga tushir
jobs -l             # fondagi joblar + PID
fg %1               # 1-jobni oldinga olib chiqish
bg %1               # to'xtatilganni fonda davom ettirish
nohup ./ish.sh &    # terminal yopilsa ham ishlashda davom etadi
```

### 4. `systemd` — servislar boshqaruvchisi
Doimiy ishlaydigan dasturlar (nginx, botlar) **servis** (unit) sifatida boshqariladi:
```
systemctl status nginx     # holati, PID, so'nggi loglar
systemctl start nginx      # ishga tushir
systemctl stop nginx       # to'xtat
systemctl restart nginx    # qayta ishga tushir
systemctl enable nginx     # boot'da avtomatik (kun-02 dan eslaysan!)
systemctl list-units --type=service   # barcha servislar
```

### 5. `journald` — markazlashgan loglar
```
journalctl -u nginx        # nginx servisining loglari
journalctl -u nginx -f     # JONLI kuzatish (yangi loglar oqib turadi, chiqish Ctrl+C)
journalctl -u nginx --since "10 min ago"
journalctl -xe             # so'nggi xatolar (debug uchun)
```

---

## 🛠️ LAB I — Jarayonlar va signallar

```bash
ps aux | head -5            # 1. jarayonlar (sarlavha + bir nechtasi)
ps aux | wc -l             # 2. nechta jarayon ishlayapti?
top                        # 3. jonli ko'r (10 soniya qara, keyin 'q')
sleep 300 &                # 4. fonda 5 daqiqalik "ish" boshla
jobs -l                    # 5. uning PID ini ko'r
pgrep -f "sleep 300"       # 6. PID ni boshqa yo'l bilan top
kill %1                    # 7. fondagi jobni to'xtat (yoki: kill <PID>)
jobs                       # 8. endi bo'shmi?
```

✅ **Lab I (+40 XP):** bajarib, "nechta jarayon ishlayapti?" javobini менga ayt.

---

## 🛠️ LAB II — systemd & journald (HAQIQIY servislar ustida!)

Eslaysanmi — biz **devops-quizbot** servisini qurgandik. Endi uni o'rgan:
```bash
systemctl status devops-quizbot     # 1. holati (active? PID? so'nggi loglar)
journalctl -u devops-quizbot -n 20  # 2. so'nggi 20 ta log
systemctl status cron               # 3. cron servisi (eslatmalaringni shu yuradi)
systemctl status ssh                # 4. ssh — sen ulanган servis
systemctl list-units --type=service --state=running | head   # 5. ishlayotgan servislar
```

✅ **Lab II (+40 XP):** `devops-quizbot` "active (running)" mi? journalda nima yozilgan? Менга ayt.

> ⚠️ Hozircha `restart`/`stop` qilma — bu ishlab turgan botlar. Faqat `status` va `journalctl`.

---

## 🧩 BOSS PUZZLE — "Signal" (XP: 250)

`days/day-03/quest/` da **guardian** qo'riqchi-jarayoni bor. Uni fonda ishga tushir,
PID ini top, va to'g'ri **signal** (SIGUSR1) yuborib xazinani och.

### Boshlash:
```
cd ~/devops/days/day-03/quest
cat START.txt
```

Zanjir: `./guardian.sh &` → `pgrep`/`jobs` → `kill -USR1 <PID>` → `cat flag_unlocked.txt`.

### G'alaba:
```
devops flag DEVOPS{...}
```
- Hint'siz → 🏆 **Process Whisperer** achievement + 250 XP
- Oxirida qo'riqchini to'xtatishni unutma: `kill <PID>` (tozalash — yaxshi odat!)

---

## 🆘 HINTS
<details><summary>Hint 1 — fonda ishga tushirish</summary>
`./guardian.sh &` — oxiridagi `&` jarayonni fonga qo'yadi. U PID chiqaradi.
</details>
<details><summary>Hint 2 — PID ni topish</summary>
`pgrep -f guardian` yoki `jobs -l`. PID — jarayonning raqami.
</details>
<details><summary>Hint 3 — signal yuborish</summary>
`kill -USR1 <PID>` (oddiy `kill` emas, `-USR1` bilan!). Keyin `cat flag_unlocked.txt`.
</details>

---

## 🎁 BONUS (+60 gacha)
1. **+20** — `ps aux --sort=-%mem | head -5` — eng ko'p XOTIRA ishlatayotgan 5 jarayon. Qaysi 1-chi?
2. **+20** — SIGTERM (15) va SIGKILL (9) farqini менга tushuntir. Qachon qaysi biri?
3. **+20** — `uptime` va `free -h` — server qancha vaqt ishlayapti va xotira holati qanday?

---

## 🔐 SECRET (+50)
Yangi yashirin xazina ekildi. Bu safar uni **jarayon/log mavzusiga** bog'ladim.
Maslahat: `grep -rl "SECRET{" ~/devops 2>/dev/null` — SECRET'ni o'z ichiga olgan faylni top.
Topib `SECRET{...}` ni менga ayt.

---

## 🐍 PYTHON DROP (+20)
**Mavzu:** funksiyalar. `labs/day-03/day03.py`:
```python
def status(name, running):
    holat = "✅ faol" if running else "❌ nofaol"
    return f"{name}: {holat}"

print(status("nginx", True))
print(status("db", False))
```
**Challenge:** servislar dict'ini aylanib (kun-02 dan), har biriga `status()` ni qo'lla.

---

## 🇬🇧 ENGLISH DROP (+15)
| So'z | Ma'no |
|------|-------|
| **process** | jarayon |
| **service** | servis (doimiy dastur) |
| **restart** | qayta ishga tushirish |
| **crash** | qulash (kutilmagan to'xtash) |
| **log** | qayd (yozuv) |

2 jumla inglizcha (`tracks/english/day03.md`): bugun servis bilan nima qilding?

---

## 💻 SHELL DRILL (+20)
**Vazifa:** eng ko'p **CPU** ishlatayotgan 3 jarayonni bir qatorda chiqar.
Maslahat: `ps aux --sort=-%cpu | head`. `tracks/shell/day03.sh` ga saqla.

---

## 📲 QUIZ (+30)
```
devops quiz today
```
Kamida 15 ta. (Telegram'da bot ham yuboradi.)

---

## ✅ DONE & XP

| Vazifa | XP |
|--------|----|
| ⬜ Lab I | +40 |
| ⬜ Lab II | +40 |
| ⬜ Boss (flag) | +250 |
| ⬜ Bonus | +60 |
| ⬜ 🔐 Secret | +50 |
| ⬜ 🐍 Python | +20 |
| ⬜ 🇬🇧 English | +15 |
| ⬜ 💻 Shell | +20 |
| ⬜ Quiz | +30 |

Tugatgach: **`devops done`** + менга **"day-03 tugatdim"**.

---

## 🔗 ERTAGA
**Day-04:** Paket boshqaruvi (`apt`) va matn qayta ishlash ustalari — `grep`, `sed`,
`awk`, pipe. "Minglab qatorli logdan kerakli ma'lumotni bir buyruqda qanday sug'urib olaman?"
