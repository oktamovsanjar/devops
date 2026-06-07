# Cheat-sheet: git

# Git Cheat Sheet

## 🔧 Sozlash / Setup
```
git config --global user.name "Ism"     — global foydalanuvchi nomi
git config --global user.email "@mail"  — global email
git config --list                        — barcha sozlamalarni ko'rish
```

## 📁 Repo Boshlash / Init
```
git init                  — yangi repo yaratish
git clone <url>           — masofaviy reponi nusxalash
git clone <url> folder    — ma'lum papkaga nusxalash
```

## 📸 Snapshot / Stage & Commit
```
git status                — o'zgarishlar holatini ko'rish
git add <file>            — faylni stage qilish
git add .                 — barcha fayllarni stage qilish
git add -p                — qismlab stage qilish (interactive)
git commit -m "msg"       — commit qilish
git commit -am "msg"      — stage + commit (tracked fayllar)
git commit --amend        — oxirgi commitni tahrirlash
```

## 🌿 Branch / Shox
```
git branch                — branchlar ro'yxati
git branch <name>         — yangi branch yaratish
git switch <name>         — branchga o'tish
git switch -c <name>      — yaratib, o'tish
git branch -d <name>      — branchni o'chirish
git branch -m <old> <new> — branchni qayta nomlash
```

## 🔀 Merge & Rebase
```
git merge <branch>        — branchni birlashtirish
git merge --no-ff <br>    — har doim merge commit yaratish
git rebase <branch>       — commitlarni qayta qurish
git rebase -i HEAD~3      — oxirgi 3 commitni interaktiv tahrir
git cherry-pick <hash>    — bitta commitni ko'chirish
```

## ⏪ Bekor Qilish / Undo
```
git restore <file>        — unstaged o'zgarishni bekor qilish
git restore --staged <f>  — stage'dan chiqarish
git reset HEAD~1          — oxirgi commitni bekor (o'zgarish qoladi)
git reset --hard HEAD~1   — oxirgi commitni butunlay o'chirish
git revert <hash>         — commitni yangi commit bilan bekor qilish
git clean -fd             — untracked fayl/papkalarni o'chirish
```

## 🕵️ Tarix / Log & Diff
```
git log                   — commit tarixi
git log --oneline --graph — qisqa, chiroyli daraxt ko'rinish
git log -p <file>         — fayl bo'yicha o'zgarishlar tarixi
git diff                  — unstaged farqlar
git diff --staged         — staged farqlar
git diff <br1>..<br2>     — ikki branch farqi
git blame <file>          — har qatorni kim yozganini ko'rish
git show <hash>           — commit tafsilotlari
```

## 📦 Stash / Vaqtinchalik Saqlash
```
git stash                 — o'zgarishlarni vaqtincha yashirish
git stash push -m "nom"   — nom bilan saqlash
git stash list            — stash ro'yxati
git stash pop             — oxirgi stashni qaytarish
git stash apply stash@{2} — ma'lum stashni qo'llash
git stash drop stash@{0}  — stashni o'chirish
```

## 🌐 Remote / Masofaviy
```
git remote -v                     — remote'lar ro'yxati
git remote add origin <url>       — remote qo'shish
git remote set-url origin <url>   — remote URL o'zgartirish
git fetch origin                  — yuklab olish (merge yo'q)
git pull origin main              — fetch + merge
git pull --rebase origin main     — fetch + rebase
git push origin <branch>          — branch yuborish
git push -u origin <branch>       — yuborish + tracking sozlash
git push --force-with-lease       — xavfsiz force push
git push origin --delete <branch> — remote branchni o'chirish
```

## 🏷️ Tag
```
git tag                     — teglar ro'yxati
git tag v1.0                — oddiy teg yaratish
git tag -a v1.0 -m "msg"    — annotated teg
git push origin v1.
