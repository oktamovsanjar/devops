# Day-18 — Docker Compose (to'liq kun)

### 🎯 Bugungi maqsad
Ko'p konteynerli ilovani **bitta YAML fayl** bilan boshqarish: `docker compose up`.
Bir buyruq bilan butun "stack" (web + db + cache...) ko'tariladi.

> 📦 **Natija:** compose.yml yozib, ko'p servisli ilovani `docker compose up -d` bilan ishga tushirish.

> 💡 Kichik image'lar (alpine, nginx:alpine). Har stack sinovdan keyin `down` qilinadi.

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (compose.yml, up) · 2️⃣ Drill (ports, volumes, depends_on) ·
3️⃣ Asosiy (ps/logs, ko'p servis, up/down) · 4️⃣ Callback (Day-16 build, Day-17 nom bilan ulanish) ·
5️⃣ Mini-loyiha "Compose stack" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Muammo: ko'p `docker run` — qiyin
3 ta konteyner = 3 ta uzun `docker run ...` buyruq, qo'lда tarmoq/volume. Yechim — **Compose**.

### 2. docker-compose.yml
```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    depends_on:
      - db
  db:
    image: alpine
    command: sleep 600
    volumes:
      - dbdata:/var/lib/db
volumes:
  dbdata:
```

### 3. Asosiy buyruqlar
```
docker compose up -d        # butun stackни fonda ko'tar
docker compose ps           # holat
docker compose logs         # barcha servis loglari
docker compose exec web sh  # servis ичiga kirish
docker compose down         # to'xtatib o'chir (-v volume ham)
```

### 4. Compose sehri
- Bitta `up` — barcha servis + **avtomatik tarmoq** + volume.
- Servislar bir-birini **nom** bilan topadi (`web` → `db`), Day-17 tarmog'i avtomatik.
- `build: .` — image'ни Dockerfile'дан quradi (Day-16).

### 5. service nomi = host nomi
`web` ичidan `db` ga ulanasan: `ping db`, `http://db:5432` — IP shart emas.

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
