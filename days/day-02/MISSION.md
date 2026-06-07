# 🎯 MISSION DAY-02 — "Permission Denied"
### Mavzu: Linux ruxsatlari (permissions), egalik (ownership), `chmod`, `chown`, `sudo`
### Rank: 🐧 Tux Cadet · Asosiy XP: 100 · Maksimal: ~450

---

## 🗺️ BRIEFING

Agent, kecha sen serverда erkin harakat qilishni o'rganding. Bugun esa har bir
DevOps muhandisi **kuniga o'nlab marta** uchratadigan to'siqni yengasan:

```
-bash: ./deploy.sh: Permission denied
```

Bu xato — dushman emas, **himoyachi**. Linux har bir fayl va papkani kim
o'qishi/yozishi/ishga tushirishi mumkinligini qat'iy nazorat qiladi. Buni
tushunsang — serverni ham boshqarasan, ham himoya qilasan (bu DevSecOps'ga ko'prik!).

> **Real kontekst:** CI/CD skriptingiz "Permission denied" berdi. Servis logni
> o'qiy olmayapti. Fayl egasi noto'g'ri. Bularning hammasi — ruxsatlar. Bugun
> ularni **ustadek** boshqarasan.

---

## 📚 LEARN (asosiy konseptlar)

### 1. `ls -l` ni o'qish — har belgi ma'no
```
-rwxr-xr--  1  ubuntu  devops  4096  Jun 4 12:00  deploy.sh
│└┬┘└┬┘└┬┘     └──┬─┘  └──┬─┘
│ │  │  │         │       └─ guruh (group)
│ │  │  │         └───────── egasi (owner/user)
│ │  │  └─ boshqalar (others): r--  = faqat o'qish
│ │  └──── guruh (group):      r-x  = o'qish + ishga tushirish
│ └─────── egasi (user):       rwx  = o'qish+yozish+ishga tushirish
└───────── tur: -=fayl, d=papka, l=symlink
```

### 2. Uchta huquq × uchta toifa
| Huquq | Harf | Faylда | Papkada |
|-------|------|--------|---------|
| read | `r` | ichini o'qish | ro'yxatini ko'rish (`ls`) |
| write | `w` | o'zgartirish | ichida fayl yaratish/o'chirish |
| execute | `x` | ishga tushirish | ichiga kirish (`cd`) |

Toifalar: **u**=user(ega), **g**=group, **o**=others, **a**=all.

### 3. `chmod` — ikki uslub
**Symbolic (harfli):**
```
chmod +x script.sh        # hammaga execute qo'sh
chmod u+w,o-r fayl        # egaga write qo'sh, boshqalardan read olib tashla
chmod g+rw fayl           # guruhga read+write
```
**Octal (raqamli):** `r=4, w=2, x=1` → qo'shamiz:
```
chmod 755 fayl   # rwx r-x r-x  (skript/papka uchun klassik)
chmod 644 fayl   # rw- r-- r--  (oddiy fayl uchun klassik)
chmod 600 fayl   # rw- --- ---  (maxfiy: faqat ega)
chmod 700 fayl   # rwx --- ---  (faqat ega hammasi)
```
> 💡 7=rwx, 6=rw, 5=r-x, 4=r. Yodla: **r=4, w=2, x=1**, qo'shib chiqar.

### 4. Egalik: `chown` / `chgrp`  (odatda `sudo` kerak)
```
sudo chown ubuntu fayl          # egasini o'zgartir
sudo chown ubuntu:devops fayl   # ega:guruh
sudo chgrp devops fayl          # faqat guruh
```

### 5. `sudo` — vaqtincha root (superuser) huquqi
```
sudo cat /etc/shadow      # oddiy user o'qiy olmaydi, root o'qiydi
```
> ⚠️ **Ega bo'lsang ham**, ruxsat 000 bo'lsa o'qiy olmaysan! (root'dan tashqari).
> Bu bugungi boss puzzle'ning siri 😉

---

## 🛠️ LAB I — Ruxsatlarni o'qish va o'zgartirish

```bash
cd ~/devops/labs/day-02 2>/dev/null || mkdir -p ~/devops/labs/day-02 && cd ~/devops/labs/day-02
echo "salom" > test.txt          # 1. fayl yarat
ls -l test.txt                   # 2. ruxsatini o'qi (qaysi rwx?)
chmod 600 test.txt; ls -l test.txt   # 3. faqat ega
chmod 644 test.txt; ls -l test.txt   # 4. ega rw, boshqalar r
echo 'echo ishladi' > run.sh     # 5. skript yarat
./run.sh                         # 6. Permission denied! (nega?)
chmod +x run.sh && ./run.sh      # 7. endi ishladi
```

✅ **Lab I (+40 XP):** 7 qadamni bajarib, 6-qadam nega xato berganini менga ayt.

---

## 🛠️ LAB II — Egalik va sudo

```bash
cd ~/devops/labs/day-02
sudo touch root_file.txt         # 1. root nomidan fayl yarat
ls -l root_file.txt              # 2. egasi kim? (root!)
echo "test" > root_file.txt      # 3. Permission denied! (sен root emassan)
sudo chown ubuntu root_file.txt  # 4. egasini o'zingга o'tkaz
echo "test" > root_file.txt && echo OK   # 5. endi yozasan
id                               # 6. o'zingning user/group laringni ko'r
grep ubuntu /etc/passwd          # 7. ubuntu user qatori
```

✅ **Lab II (+40 XP):** bajarib, `id` natijasidagi guruhlaringni менга ayt.

---

## 🧩 BOSS PUZZLE — "Qulflangan Ruxsatlar" (XP: 250)

`days/day-02/quest/` da 4 bosqichli ruxsat sinovi seni kutyapti:
`chmod +r` → `chmod +x` → `sudo`.

### Boshlash:
```
cd ~/devops/days/day-02/quest
cat START.txt
```

Har qadamni yech. Oxirida `DEVOPS{...}` flagni topasan.

### G'alaba:
```
devops flag DEVOPS{...}
```
- Hint'siz → 🏆 **Permission Master** achievement + 250 XP

---

## 🆘 HINTS

<details><summary>Hint 1 — locked.txt o'qilmayapti</summary>
Sen egasisan, lekin read (r) yo'q. `chmod +r locked.txt` (yoki `chmod 644 locked.txt`).
</details>
<details><summary>Hint 2 — reveal.sh ishlamayapti</summary>
Skript executable emas. `chmod +x reveal.sh`, keyin `./reveal.sh`.
</details>
<details><summary>Hint 3 — vault.txt root niki</summary>
`cat vault.txt` → Permission denied. Root huquqi kerak: `sudo cat vault.txt`.
</details>

---

## 🎁 BONUS (+60 gacha)
1. **+20** — `chmod 777 fayl` nima qiladi va NEGA bu **xavfli**? Менga tushuntir.
2. **+20** — `find ~/devops -type f -perm -u+x` — bu nimani topadi?
3. **+20** — `umask` buyrug'ini ishga tushir — yangi fayllar default ruxsati qayerdan kelishini bil.

---

## 🔐 SECRET (+50)
Day-01'dagidek, yangi yashirin xazina bor. Bu safar u **ruxsati o'zgartirilgan**
yashirin faylда. Maslahat: `find ~/devops -name ".*" -type f -newer ~/devops/PLAN.md 2>/dev/null`.
Topib `SECRET{...}` ni менга ayt.

---

## 🐍 PYTHON DROP (+20)
**Mavzu:** list va dict. `labs/day-02/day02.py`:
```python
servers = ["web1", "web2", "db1"]
status = {"web1": "running", "web2": "stopped", "db1": "running"}
for s in servers:
    print(f"{s}: {status[s]}")
```
**Challenge:** faqat "running" serverlarni chiqar (maslahat: `if`).

---

## 🇬🇧 ENGLISH DROP (+15)
| So'z | Ma'no | Misol |
|------|-------|-------|
| **permission** | ruxsat | "Permission denied." |
| **owner** | egasi | "Change the file owner." |
| **execute** | ishga tushirish | "Make the script executable." |
| **grant** | berish (ruxsat) | "Grant read access." |
| **deny** | rad etish | "Access denied." |

Bugungi ishni 2 jumlada inglizcha yoz (`tracks/english/day02.md`).

---

## 💻 SHELL DRILL (+20)
**Vazifa:** `~/devops` ichidagi barcha `.sh` (skript) fayllarni topib, hammasini
bir buyruqda executable qil. Maslahat: `find ... -name "*.sh" -exec chmod +x {} +`.
`tracks/shell/day02.sh` ga saqla.

---

## 📲 QUIZ (+30)
```
devops quiz today     # bugun: linux (ruxsatlar ham bor!)
```
Yoki Telegram'da bot orqali. Kamida 15 ta, 80%+ maqsad.

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

Tugatgach: **`devops done`** + менга **"day-02 tugatdim"**.

---

## 🔗 ERTAGA
**Day-03:** Jarayonlar (processes), signallar, `systemd` servislar va `journald` loglar —
"Servis o'lib qoldi, qanday qayta tiklayman va logini qayerdan ko'raman?"
