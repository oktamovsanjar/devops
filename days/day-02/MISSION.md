# Day-02 — Ruxsatlar va egalik

### 🎯 Bugungi maqsad
"Permission denied" ni tushunish va **to'g'ri** yechish. Har bir DevOps muhandisi
kuniga o'nlab marta uchratadigan narsa.

> 📦 **Natija:** fayllarga to'g'ri ruxsat (600/644/700) qo'ya olish, `sudo`ni o'rinli ishlatish.

---

## 📚 Nazariya (faqat tushuncha — topshiriqlar `devops next`da)

### 1. `ls -l` ni o'qish
```
-rwxr-xr--  ubuntu  devops   deploy.sh
│└┬┘└┬┘└┬┘  └──┬─┘  └──┬─┘
│ │  │  │     ega     guruh
│ │  │  └ others (boshqalar): r-- = faqat o'qish
│ │  └─── guruh:               r-x = o'qish + ishga tushirish
│ └────── ega:                 rwx = o'qish+yozish+ishga tushirish
└──────── tur: - fayl, d papka, l symlink
```

### 2. Uch huquq × uch toifa
| Huquq | Faylда | Papkada |
|-------|--------|---------|
| **r** (read) | ichini o'qish | ro'yxatni ko'rish (ls) |
| **w** (write) | o'zgartirish | ichida yaratish/o'chirish |
| **x** (execute) | ishga tushirish | ichiga kirish (cd) |

Toifalar: **u**=ega, **g**=guruh, **o**=boshqalar, **a**=barchasi.

### 3. `chmod` — ikki uslub
**Harfli:** `chmod +x fayl` · `chmod o-rwx fayl` (others'dan olib tashla)
**Raqamli (octal):** `r=4, w=2, x=1` qo'shib chiqar:
| Octal | Ma'no | Qachon |
|-------|-------|--------|
| `755` | rwx r-x r-x | skript / papka |
| `644` | rw- r-- r-- | oddiy fayl |
| `600` | rw- --- --- | maxfiy (faqat ega) |
| `700` | rwx --- --- | yopiq papka |

### 4. Egalik va `sudo`
```
sudo chown ubuntu:devops fayl   # ega:guruh
sudo cat /etc/shadow            # root huquqi bilan o'qish
```
> ⚠️ **Ega bo'lsang ham**, ruxsat `000` bo'lsa o'qiy olmaysan (root'dan tashqari).
> Bu bugungi BOSS jumbog'ining siri 😉

---

## ▶️ Endi ishga
```
devops next       # nima qilishni aytadi
devops verify     # AI tekshiradi → keyingisi
```
Hamma topshiriq bajarilsa — kun avtomatik yakunlanadi.
