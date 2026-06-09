# Day-15 — Konteyner asoslari + YAML (to'liq kun)

### 🎯 Bugungi maqsad
**Docker** bilan tanishish: image vs container, `docker run/ps/logs/exec`, konteynerni
boshqarish. Va **YAML** — konteyner dunyosining tili.

> 📦 **Natija:** tayyor image'ni ishga tushirish, konteyner ichiga kirish, log o'qish,
> to'xtatish/o'chirish + to'g'ri YAML yoza olish.

> 💡 Docker o'rnatilgan. Bugun kichik image'lar bilan ishlaymiz (hello-world, alpine — bir necha MB).

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (version, hello-world) · 2️⃣ Drill (pull, run, ps) ·
3️⃣ Asosiy (named/detached, logs, exec, stop/rm, YAML) · 4️⃣ Callback (Day-3 jarayon, Day-4 grep) ·
5️⃣ Mini-loyiha "Containerized" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Image vs Container
- **Image** — "qolip" (o'qish uchun shablon, masalan `alpine`).
- **Container** — image'dan ishga tushgan **tirik nusxa** (jarayon kabi).
> Bitta image'dan ko'p container yaratish mumkin.

### 2. Asosiy buyruqlar
```
docker --version              # versiya
docker pull alpine            # image yuklab ol
docker run alpine echo hi     # image'dan container ishga tushir
docker run -d --name web nginx  # -d = fonda (detached), --name = nom
docker ps                     # ishlab turgan containerlar
docker ps -a                  # hammasi (to'xtaganlar ham)
docker images                 # mavjud image'lar
```

### 3. Boshqarish
```
docker logs <nom>             # container loglari
docker exec <nom> <buyruq>    # ichida buyruq bajar (masalan: docker exec web ls /)
docker exec -it <nom> sh      # ichiga interaktiv kirish
docker stop <nom>             # to'xtat
docker rm <nom>               # o'chir   (docker rm -f = majburan)
```

### 4. Container = izolyatsiyalangan jarayon
Container — bu yengil, izolyatsiyalangan **jarayon** (Day-3 dagi process kabi, lekin
o'z fayl tizimi/tarmog'i bilan). VM emas — tezroq va yengilroq.

### 5. YAML — konteyner tili
Docker Compose, Kubernetes — hammasi YAML. Asosi:
```yaml
name: myapp           # key: value
version: "1.0"
ports:                # ro'yxat
  - 8080
  - 9090
env:                  # ichki obyekt
  DEBUG: true
```
> YAML — **bo'shliq (indentation) muhim!** Tab emas, probel.

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
