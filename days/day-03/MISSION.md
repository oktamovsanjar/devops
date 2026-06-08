# Day-03 — Jarayonlar va servislar (to'liq kun)

### 🎯 Bugungi maqsad
Serverdagi **jarayonlarni** (processes) ko'rish, boshqarish, signal yuborish; va
**systemd servislari** + **journald loglar**ni o'qish.

> 📦 **Natija:** drill bilan tezlik + shubhali jarayonni topish + "Process Monitor" mini-loyihasi.

---

## 🗓️ Bugungi kun rejasi (~7 soat, 6 blok)

| Blok | Nima | Taxminiy |
|------|------|----------|
| 1️⃣ Yo'naltirish | ps, xotira eng och jarayonlar | ~20 daq |
| 2️⃣ Drill | fon jarayon / pgrep / pkill — tezlik | ~45 daq |
| 3️⃣ Asosiy ko'nikmalar | bg/pid/kill, systemctl, journald, CPU | ~90 daq |
| 4️⃣ Callback | Day-1 grep + Day-2 chmod — jarayon ustида | ~45 daq |
| 5️⃣ Mini-loyiha | "Process Monitor" — boshidan oxirigacha qur | ~90 daq |
| 6️⃣ Yakuniy sinov | BOSS (SIGUSR1 signal) + xulosa + `devops exam` | ~60 daq |

> 🔁 **Callback bloki:** bugun Day-1 (grep) va Day-2 (chmod +x) ko'nikmalaringни jarayon
> kontekstida qayta ishlatasan — eski bilim mustahkamlanadi.

---

## 📚 Nazariya (topshiriqlar `devops next`да)

### 1. Jarayonlar (processes)
```
ps aux              # barcha jarayonlar (PID, CPU, RAM...)
ps aux | grep nginx # nom bo'yicha
top  (yoki htop)    # jonli, real-time (chiqish: q)
pgrep -f nom        # nom bo'yicha PID
```
Har jarayon — **PID** raqamiga ega. PID 1 = `systemd` (hammaning ajdodi).

### 2. Signallar (kill = signal yuborish, "o'ldirish" emas)
| Signal | № | Ma'no |
|--------|---|-------|
| SIGTERM | 15 | "chiroyli to'xta" (default) |
| SIGKILL | 9 | "majburan o'l" (oxirgi chora) |
| SIGUSR1 | 10 | dasturchi belgilagan maxsus ish |
```
kill 1234       # SIGTERM (yumshoq)
kill -9 1234    # SIGKILL (majburiy)
kill -USR1 1234 # maxsus
```

### 3. Fonda ishlatish
```
sleep 100 &     # & = orqa fonda
jobs -l         # fondagi joblar + PID
```

### 4. systemd — servislar
```
systemctl status nginx      # holat, PID, so'nggi loglar
systemctl restart nginx     # qayta tiklash
systemctl is-active nginx   # active / inactive
```

### 5. journald — loglar
```
journalctl -u nginx         # servis loglari
journalctl -u nginx -f      # jonli kuzatish (Ctrl+C)
journalctl -xe              # so'nggi xatolar
```

---

## ▶️ Endi ishga
```
devops next       # nima qilishni aytadi
devops verify     # tekshiradi → keyingisi
```
BOSS jumbog'i `devops next`да keladi.
