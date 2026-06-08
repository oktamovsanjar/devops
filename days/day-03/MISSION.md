# Day-03 — Jarayonlar va servislar

### 🎯 Bugungi maqsad
Serverdagi **jarayonlarni** (processes) ko'rish, boshqarish, signal yuborish; va
**systemd servislari** + **journald loglar**ni o'qish.

> 📦 **Natija:** o'lik servisni topib, sababini logдан bilib, qayta tiklash mahorati.

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
