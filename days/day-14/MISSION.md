# Day-14 — 🏁 2-hafta BOSS: Deploy (hammasini birlashtirish)

### 🎯 Bugungi maqsad
2-haftaning **yakuniy sinovi**: bash II, cron, git, tarmoq, nginx — hammasini
bitta **real deploy loyihasида** birlashtirasan.

> 📦 **Natija:** git'ga olingan ilova + robust deploy skripti + nginx config +
> health-check + cron avtomatlashtirish — to'liq "deploy" tizimi.

---

## 📚 Bu hafta nimani o'rganding (qisqa takror)

| Day | Mavzu | Asosiy |
|-----|-------|--------|
| 8 | Bash II | `getopts`, `trap`, `set -e` |
| 9 | Cron | rejalashtirilgan ishlar, backup |
| 10 | Git | `commit`, `branch`, `merge` |
| 11 | Git jamoa | remote, PR, conflict |
| 12 | Tarmoq | DNS, TLS, HTTP debug |
| 13 | Nginx | reverse proxy, TLS config |

Bugun shularning hammasini ishlatasan.

---

## 🏗️ Bugungi loyiha: "Deploy tizimi"
```
deploy/
├── .git/                 # git (Day-10/11)
├── app/index.html        # ilova
├── bin/deploy.sh         # robust deploy skripti (Day-8: set -e, arg)
├── bin/health.sh         # health-check (Day-12: curl + Day-13: config tekshir)
├── config/site.conf      # nginx reverse proxy (Day-13)
└── config/cron.txt       # avtomatlashtirish (Day-9)
```

Har qadam — bir haftalik ko'nikmaning amaliyoti.

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Hammasi tugasa — **2-hafta yakunlanadi**, Day-15 (Docker) ochiladi! 🎉
So'ng:  `devops exam`  +  `devops checkpoint bash`  (mastery-gate).
