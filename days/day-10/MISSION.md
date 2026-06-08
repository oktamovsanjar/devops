# Day-10 — Git asoslari (to'liq kun)

### 🎯 Bugungi maqsad
Kodni **versiyalash**: `git init/add/commit`, tarmoqlar (`branch/merge`), `.gitignore`.
Har bir DevOps muhandisining kundalik quroli.

> 📦 **Natija:** loyihani git'ga olib, tarix yuritish, branch'да ishlab, merge qilish.

> 💡 Bugun hammasi LOKAL repo'да (work/ ичида) — internet kerak emas.

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (init, config) · 2️⃣ Drill (add, commit, log) ·
3️⃣ Asosiy (branch, merge, .gitignore, diff) · 4️⃣ Callback (Day-1 tuzilma, Day-8 skript) ·
5️⃣ Mini-loyiha "Versioned Project" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Git nima?
Kod **tarixini** saqlaydigan tizim — har o'zgarishni "snapshot" (commit) qilib qo'yadi.
Adashsang — orqaga qaytasan; jamoa bilan — parallel ishlaysan.

### 2. Asosiy oqim
```
git init                 # repo yaratish
git config user.name "X" # kim (lokal)
git add fayl             # staging'ga qo'sh
git commit -m "xabar"    # snapshot saqla
git log --oneline        # tarix
git status               # holat
```
> **add** = "shu o'zgarishni keyingi commitga tayyorla" · **commit** = "saqlab qo'y".

### 3. Branch (tarmoq)
```
git branch feature       # yangi tarmoq
git checkout feature     # unga o't  (yoki: git switch feature)
git checkout main        # asosiy tarmoqqa qayt
git merge feature        # feature'ni asosiyga qo'sh
```

### 4. .gitignore
```
echo "secret.txt" >> .gitignore   # bu fayl git'ga KETMAYDI
echo "*.log"      >> .gitignore
```
> Maxfiy fayllar (parol, kalit, .env) HECH QACHON commit qilinmasin.

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
