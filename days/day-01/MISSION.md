# Day-01 — Linux navigatsiya

### 🎯 Bugungi maqsad
Serverda **erkin harakat qilish**: qayerda nima turishini bilish, fayl topish va
o'qish. Bu — qolgan hamma narsaning poydevori.

> 📦 **Natija:** tartibli ish maydoni + server hujjati + logdan xatolarni ajratish.

---

## 📚 Nazariya (faqat tushuncha — topshiriqlar `devops task`da)

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
| `cat` / `less` | fayl o'qish |
| `grep` | matn ichidan qidirish |
| `find` | fayl qidirish |
| `>` / `>>` | natijani faylga yozish (ustiga / qo'shib) |
| `man <buyruq>` | qo'llanma |

> 💡 Oltin qoida: buyruqни bilmasang — `man buyruq` yoki `buyruq --help`. Yodlama, qarab ol.

---

## ▶️ Endi ishga
Nazariyani o'qiding — **topshiriqlarga o't:**
```
devops task          # bugungi topshiriqlar (boy, avto-tekshiriladi)
devops task 1        # birinchisini batafsil ko'r
devops task check    # bajarganingni tekshir
```
Jumboq (BOSS) `devops task`da 5-topshiriq sifatida ko'rsatilgan.
Kun tugagach: `devops done`.
