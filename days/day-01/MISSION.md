# Day-01 — Linux navigatsiya (to'liq kun)

### 🎯 Bugungi maqsad
Serverda **erkin harakat qilish**: qayerda nima turishini bilish, fayl topish, o'qish,
qidirish va natijani saqlash. Bu — qolgan hamma narsaning poydevori.

> 📦 **Natija:** drill bilan tezlik + tartibli ish maydoni + buzuqni tuzatish + "Server Inventory" mini-loyihasi.

---

## 🗓️ Bugungi kun rejasi (~7 soat, 6 blok)

| Blok | Nima | Taxminiy |
|------|------|----------|
| 1️⃣ Yo'naltirish | pwd, ls — qayerdaman | ~20 daq |
| 2️⃣ Drill | mkdir/touch/glob/tail — tezlik mashqi | ~45 daq |
| 3️⃣ Asosiy ko'nikmalar | inventory, log triage, find | ~90 daq |
| 4️⃣ Troubleshooting | buzuqni topib tuzat (grep -r, skript, disk) | ~60 daq |
| 5️⃣ Mini-loyiha | "Server Inventory" — boshidan oxirigacha qur | ~90 daq |
| 6️⃣ Yakuniy sinov | BOSS quest + xulosa + `devops exam` | ~60 daq |

`devops next` seni blokma-blok olib boradi. Shoshma — har blok oldingisini mustahkamlaydi.

---

## 📚 Nazariya (tushuncha — topshiriqlar `devops next`da)

### 1. Fayl tizimi — bitta daraxt
Linuxда hamma narsa `/` (root) dan boshlanadigan bitta daraxt. `C:`, `D:` yo'q.
Har disk shu daraxtning bir shoxiga "ulanadi" (mount).

### 2. Muhim papkalar (FHS)
| Papka | Nima |
|-------|------|
| `/etc` | konfiguratsiya fayllari |
| `/var/log` | loglar |
| `/home` | foydalanuvchi uyi |
| `/bin`, `/usr/bin` | buyruqlar |
| `/tmp` | vaqtinchalik |

### 3. Yo'llar
- **Absolute:** `/` dan → `/var/log/syslog` (har joydan ishlaydi)
- **Relative:** turgan joyingдан → `logs/today.txt`
- `.` = shu papka · `..` = bir yuqori · `~` = uy · `-` = oldingi

### 4. Asosiy buyruqlar
| Buyruq | Vazifa |
|--------|--------|
| `pwd` | qayerdaman? |
| `ls -la` | papkani ko'rsat (batafsil + yashirin) |
| `cd` | papkaga o't |
| `cat` / `head` / `tail` | fayl o'qish (boshi / oxiri) |
| `grep` | matn ichidan qidirish |
| `find` | fayl qidirish |
| `>` / `>>` | natijani faylga yozish (ustiga / qo'shib) |
| `man <buyruq>` | qo'llanma |

### 5. Wildcard (glob) — namuna bo'yicha tanlash
Shell fayl nomlarini namunaga ko'ra o'zi to'ldiradi:
- `*` = istalgan belgilar → `*.log` (barcha .log), `app*` (app bilan boshlanadi)
- `?` = bitta belgi → `file?.txt` (file1.txt, fileA.txt...)
- `[1-3]` = oraliq → `file[1-3].txt` (file1,2,3)
- `{1..10}` = ketma-ketlik → `touch file{1..10}.txt` (10 ta fayl bir zarbда)

### 6. Redirection — natijani boshqarish
| Belgi | Ma'no |
|-------|-------|
| `>` | chiqishni faylga yoz (ustiga yozadi!) |
| `>>` | faylga qo'shib yoz |
| `2>` | XATO oqimini (stderr) yo'naltir |
| `\|` | bir buyruq chiqishini boshqasiga uzat (pipe) |

Misol:  `ls -S /var/log | head -3 > biggest.txt`  →  saralab, eng katta 3 tasini saqla.

### 7. Qidiruv — `find` va `grep` farqi
- **`find`** — FAYLNI topadi (nom, hajm, vaqt bo'yicha):
  `find /var/log -name "*.log" -size +50k`  (50KB dan katta .log lar)
- **`grep`** — fayl ICHIDAN matn qidiradi:
  `grep ERROR app.log`  ·  `grep -r needle papka/`  (-r = ichki papkalar ham, -l = faqat fayl nomi)

> 💡 Oltin qoida: buyruqни bilmasang — `man buyruq` yoki `buyruq --help`. Yodlama, qarab ol.

---

## ▶️ Endi ishga
```
devops next       # blokma-blok olib boradi + ish-papkani ko'rsatadi
devops verify     # bajarganingni tekshiradi → keyingisiga o'tkazadi
```
Hamma topshiriq bajarilsa — kun avtomatik yakunlanadi. So'ng amaliy imtihon:
```
devops exam       # hintsiz, qattiq nazorat — kunni mustahkamlaydi
```
