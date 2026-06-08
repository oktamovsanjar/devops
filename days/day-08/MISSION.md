# Day-08 — Bash skripting II (to'liq kun)

### 🎯 Bugungi maqsad
Skriptlarni **mustahkam** (robust) qilish: argumentlar, flaglar (`getopts`), xato
boshqaruvi (`set -e`, exit kodlar), tozalash (`trap`). Bu — real avtomatlashtirish.

> 📦 **Natija:** argumentli, xatoga chidamli, o'zini tozalaydigan skript yozish.

---

## 🗓️ Bugungi kun rejasi (~7 soat, 6 blok)

| Blok | Nima | Taxminiy |
|------|------|----------|
| 1️⃣ Yo'naltirish | exit kod ($?), set -e | ~20 daq |
| 2️⃣ Drill | $#, $@, default qiymat | ~45 daq |
| 3️⃣ Asosiy | getopts, trap, funksiya, validatsiya | ~90 daq |
| 4️⃣ Callback | Day-3 ps + Day-1 find — robust skriptда | ~45 daq |
| 5️⃣ Mini-loyiha | "Robust Script" — argumentli, xatoga chidamli | ~90 daq |
| 6️⃣ Yakuniy sinov | xulosa + `devops exam` | ~60 daq |

---

## 📚 Nazariya (topshiriqlar `devops next`да)

### 1. Exit kod — muvaffaqiyatmi?
Har buyruq tugagach **exit kod** qoldiradi:  `0` = OK, `≠0` = xato.
```
ls /yoq 2>/dev/null;  echo $?     # $? = oxirgi buyruq kodi (masalan 2)
```

### 2. Qattiq rejim (xato boshqaruvi)
```
set -e            # birinchi xatoда skript to'xtaydi
set -u            # aniqlanmagan o'zgaruvchi = xato
set -o pipefail   # pipe'да birorta bo'g'in yiqilsa — xato
```
> Professional skriptlar ko'pincha:  `set -euo pipefail`

### 3. Argumentlar
| Belgi | Ma'no |
|-------|-------|
| `$1 $2` | 1-, 2- argument |
| `$#` | argumentlar SONI |
| `$@` | hamma argument (alohida) |
| `"$@"` | to'g'ri tirnoqlangan hamma argument |
| `${1:-default}` | $1 bo'sh bo'lsa — default |

### 4. getopts — flaglar
```
while getopts "n:v" opt; do
  case $opt in
    n) name=$OPTARG ;;   # -n qiymat
    v) verbose=1 ;;      # -v (qiymatsiz)
  esac
done
```

### 5. Funksiya: return vs echo
- `echo` → natijani **chiqaradi** (matn)
- `return N` → funksiyaning **exit kodini** beradi (0-255)

### 6. trap — tozalash
```
trap 'rm -f /tmp/lock; echo "tozalandi"' EXIT   # skript tugaganда (xato bo'lsa ham) ishlaydi
```

---

## ▶️ Endi ishga
```
devops next       # blokma-blok olib boradi
devops verify     # tekshiradi → keyingisi
```
Kun tugagach:  `devops exam`  (hintsiz amaliy imtihon).
