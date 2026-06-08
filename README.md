# 🚀 DevOps Bootcamp — Shtab-kvartira

> **Maqsad:** 0 dan chuqur fundament bilan **Junior DevOps Engineer** bo'lish.
> **Temp:** ~2 oy intensiv · 7-8 soat/kun · amaliyot + jumboq + mission formati.
> **Ustoz:** Claude (shu terminalda, har kuni yoningda).

---

## 📂 Fayl iyerarxiyasi (aniq tuzilma)

```
devops/
├── CURRICULUM.md      # 📚 To'liq 56 kunlik master-reja (har kun maqsadi + natijasi)
├── PLAN.md            # 8 haftalik qisqa ko'rinish
├── SCHEDULE.md        # Kunlik/haftalik kun tartibi
├── README.md          # shu fayl
│
├── days/              # ⭐ HAR KUN — BITTA PAPKA (hammasi shu yerda)
│   └── day-02/
│       ├── MISSION.md   # nazariya (faqat tushuncha)
│       ├── tasks.json   # topshiriqlar (yagona manba, avto-tekshiriladi)
│       ├── work/        # 🛠️ SENING ish joying (fayllaringni shu yerda yarat)
│       ├── quest/       # 🧩 jumboq (boss puzzle)
│       ├── fixtures/    # tayyor namuna fayllar (ba'zi kunlar)
│       └── exam/        # imtihon ish joyi
│
├── engine/            # CLI yadrosi: cli.py, AI, SRS, savol banki
├── scripts/           # Telegram bot, monitoring
├── tracks/            # Python / English / Shell parallel treklar
└── resources/         # cheat-sheet'lar, qo'shimcha
```

> 🎯 **Asosiy qoida:** bir kun = bir papka (`days/day-XX/`). Ishni shu kunning
> `work/` papkasida qilasan — boshqa joyga sakrab yurmaysan.

---

## 🎮 O'yin qoidalari (qanday ishlaydi)

Har kun bitta **MISSION** (`days/day-XX/MISSION.md`). Har mission'da:

1. 🗺️ **Briefing** — bugun nimani va NEGA o'rganamiz (real ish konteksti)
2. 📚 **Learn** — qisqa, aniq nazariya (faqat kerakligi)
3. 🛠️ **Labs** — qo'l bilan bajariladigan amaliy vazifalar
4. 🧩 **Boss puzzle** — kunni yakunlovchi jumboq (haqiqiy tushunishni sinaydi)
5. 🆘 **Hints** — qotib qolsang, maslahatlar (avval o'zing urin!)
6. ✅ **Done & XP** — yakunlash mezoni va olingan ball

### Ballar va daraja
- Har vazifa **XP** beradi. Boss puzzle ko'proq beradi.
- XP yig'ilib **rank** (daraja) ko'tariladi: 🐧 → 🎖️ (8 daraja).
- Har kun bajarsang **streak 🔥** o'sadi. Streak uzilmasligi — intizom mezoni.
- To'liq jadval: [PROGRESS.md](PROGRESS.md).

### "Skip-test" (bilganini tez o'tish)
Allaqachon bilaman degan kuningda — **avval Boss puzzle'ni yech**. Yechsang,
o'sha kun XP to'liq beriladi va labs'ni o'tkazib yuborishing mumkin. Bu sening
"ba'zi narsalarni bilaman" deganingni hisobga oladi — bilganingda vaqt yo'qotmaysan,
bilmaganingda chuqur o'rganasan.

---

## 🛰️ Full Monitoring (terminal faoliyating yozib boriladi)

Bu serverda har **interaktiv buyrug'ing** timestamp + papka + exit-code bilan
avtomatik log qilinadi (`logs/activity/`). Bu — real DevOps'dagi *audit logging*ning
mini versiyasi va sening mehnatingni o'lchaydi.

```bash
python3 scripts/monitoring/day-report.py            # bugungi hisobot: faol vaqt, buyruqlar, xatolar, top qurollar
python3 scripts/monitoring/day-report.py --telegram # hisobotni Telegram'ga yuborish
```
> ⚙️ `.bashrc` ga o'rnatildi — **yangi terminal ochsang avtomatik ishlaydi**.

## 🐍🇬🇧💻 Parallel Skill-Treklar

Asosiy DevOps mission yonida har kuni qisqa mini-mashqlar (mission ichida keladi):
- 🐍 [tracks/python/](tracks/python/) — Python for DevOps (avtomatlashtirish)
- 🇬🇧 [tracks/english/](tracks/english/) — Tech English (docs, error, intervyu)
- 💻 [tracks/shell/](tracks/shell/) — Shell scripting mahorat

## 🎁 Bonus · 🔐 Secret · 📲 Quiz

- **🎁 Bonus vazifalar** — har mission'da qo'shimcha XP uchun ixtiyoriy challenge'lar
- **🔐 Secret'lar** — butun bootcamp bo'ylab yashirin xazinalar (`.` bilan boshlanadi). Topgan — bonus XP + achievement 🕵️
- **📲 Telegram quiz** — kunlik test savollari:
  ```bash
  python3 scripts/telegram/quiz.py linux   # bugungi mavzudan quiz yuborish
  ```

## ▶️ Har kuni qanday boshlash — `devops` buyrug'i

Terminal — sening boshqaruv markazing. Har kun shu tartibda:

```bash
devops today      # ❶ "Men kirdim — bugun nima qilaman?" — kun, vaqt, muhlat, ish
devops start      # ❷ Kunni boshlash (vaqt hisobi + muhlat yoqiladi)
devops task       # ❸ Bugungi topshiriqlar ro'yxati  (devops task done <N> = bajarildi)
devops lab        # ❹ Bugungi laboratoriya (ishchi papkang: days/day-XX/work/)
devops quiz       # ❺ Cheksiz quiz/drill oqimi
devops review     # ❻ SRS — eski mavzularni takror (unutmaslik uchun)
devops deadline   # ⏳ Muhlat va bugun ishlangan vaqt
devops done       # 🏁 Kunni yakunlash (keyingi kunga o'tadi)
devops profile    # 🧑‍🚀 Men haqimda: kuchli/zaif mavzular, vaqt, progress
```

> 🧪 **"Laboratoriya" nima?** — Bu **serverning O'ZI** sening laboratoriyang!
> DevOps real tizimda o'rganiladi, alohida sandbox shart emas. Har kun uchun
> `days/day-XX/work/` ishchi papkasi tayyorlanadi — fayllaringni shu yerda yarat.

Bularning ustiga, men (Claude/ustoz) har doim shu terminalда: mission'ni
tushuntiraman, ishingni tekshiraman, qotsang yordam beraman. Istalgan payt:
**"ustoz, ..."** deb yoz. Kun yakunida: **"day-XX tugatdim"**.

Boshlash uchun **hozir:** `devops today`

---

## 🧭 Yo'l (katta rasm)

`DevOps` (bu bootcamp) → keyin `+Security = DevSecOps` → `SRE` → `Cloud Security`.
Hozir **faqat DevOps**ga fokus. Chalg'imaymiz. Har biri uchun alohida bootcamp bo'ladi.
