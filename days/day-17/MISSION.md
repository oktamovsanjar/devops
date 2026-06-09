# Day-17 — Volume, network, debug (to'liq kun)

### 🎯 Bugungi maqsad
Konteynerlarni **bog'lash** va **ma'lumotini saqlash**: volume (doimiy data), network
(konteynerlar bir-biri bilan gaplashishi), port, va debug (inspect/stats).

> 📦 **Natija:** ma'lumot saqlanadigan konteyner + tarmoqда bir-birini topadigan konteynerlar.

> 💡 Kichik image'lar (alpine, nginx:alpine) bilan. Hammasi tozalanadi.

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (volume, network ls) · 2️⃣ Drill (bind mount, volume/net create) ·
3️⃣ Asosiy (volume persist, nom bilan ulanish, port, inspect/stats) ·
4️⃣ Callback (Day-8 skript, Day-4 grep) · 5️⃣ Mini-loyiha "Data+Network" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Muammo: konteyner o'chsa — ma'lumot yo'qoladi
Konteyner ичiдаги fayllar vaqtinchalik. `docker rm` qilsang — yo'qoladi. Yechim — **volume**.

### 2. Volume — doimiy ma'lumot
```
docker volume create mydata               # nomli volume
docker run -v mydata:/var/lib/db ...       # konteynerга ulash
# konteyner o'chsa ham, mydata ичidagi ma'lumot QOLADI
```
**Bind mount** — host papkasini ulash:
```
docker run -v /home/ubuntu/app:/app ...    # host papka <-> konteyner
docker run -v "$PWD/data":/data alpine ...
```

### 3. Network — konteynerlar gaplashadi
```
docker network create mynet                # tarmoq yarat
docker run -d --name db --network mynet ...
docker run --network mynet alpine ping db  # NOM bilan topadi! (DNS)
```
> Bitta user-network'дagi konteynerlar bir-birini **nom** bilan topadi (IP shart emas).

### 4. Port — tashqariga ochish
```
docker run -d -p 8080:80 nginx     # host:8080 -> konteyner:80
curl localhost:8080                # tashqaridan ko'rinadi
docker port <nom>                  # qaysi portlar ochiq
```

### 5. Debug
```
docker logs <nom>            # chiqishlar
docker exec -it <nom> sh     # ichiga kirish
docker inspect <nom>         # to'liq JSON (IP, mount, env...)
docker stats --no-stream     # CPU/RAM iste'moli
```

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
