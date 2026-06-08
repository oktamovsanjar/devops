# Day-11 — Git jamoa: remote, push/pull, PR, conflict (to'liq kun)

### 🎯 Bugungi maqsad
Jamoa bilan ishlash: **remote**ga `push`/`pull`, **Pull Request** oqimi, va eng
muhimi — **conflict** (to'qnashuv)ni yechish.

> 📦 **Natija:** remote'ga push, feature branch'ни merge qilish, conflict'ni qo'lda yechish.

> 💡 Bugun "remote" ni LOKAL **bare repo** bilan simulyatsiya qilamiz (GitHub mantig'i
> aynan shu — internet/akkaunt shart emas, xavfsiz mashq).

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (bare repo, clone) · 2️⃣ Drill (push, remote, sync) ·
3️⃣ Asosiy (conflict yaratish/yechish, PR-merge) · 4️⃣ Callback (Day-10 .gitignore, Day-8 skript) ·
5️⃣ Mini-loyiha "Team Workflow" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Remote — markaziy repo
```
git clone <url> papka       # remote'dan nusxa olish
git remote -v               # ulanган remote'lar
git push origin <branch>    # o'zgarishni remote'ga yuborish
git pull                    # remote'dan yangilik olish
```
> "bare" repo (`git init --bare`) — ishchi nusxasiz, faqat tarix saqlovchi (markaz).

### 2. Pull Request (PR) oqimi
```
git checkout -b feature     # 1. feature branch
# ... ishla, commit ...
git push origin feature     # 2. remote'ga push
# 3. GitHub'da PR ochasan → ko'rib chiqiladi → merge
git checkout main && git merge feature   # (lokalда merge mantig'i)
```

### 3. Conflict (to'qnashuv) — qachon?
Ikki kishi **bir qatorni** o'zgartirsa, git o'zi hal qila olmaydi:
```
<<<<<<< HEAD
sening o'zgarishing
=======
boshqaning o'zgarishi
>>>>>>> feature
```
**Yechish:** faylни ochib, kerakli variantni qoldir, belgilarni (`<<<`, `===`, `>>>`)
o'chir, keyin:  `git add fayl && git commit`.

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
