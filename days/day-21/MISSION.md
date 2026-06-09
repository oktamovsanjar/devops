# Day-21 — 🏁 3-hafta BOSS: Multi-servis stack

### 🎯 Bugungi maqsad
3-haftaning **yakuniy sinovi**: web ilova + cache (redis) ni **bitta compose stack**
qilib, volume + network + registry bilan to'liq ishga tushirasan. Butun Docker
ko'nikmangни bitta real "stack"да birlashtirasan.

> 📦 **Natija:** `docker compose up` bilan ko'tariladigan ko'p-servisli ilova +
> servislar nom bilan bog'langan + registry'ga tayyor.

> 🧗 Narvon: 📖 → 🛠️ qadamli → 🎯 mustaqil → 🧠 quiz → 🎓 exam → 🎤 interview → 💬 suhbat.

---

## 📚 Bu hafta (Docker) — qisqa takror
| Day | Ko'nikma |
|-----|----------|
| 15 | run/ps/logs/exec |
| 16 | Dockerfile (build) |
| 17 | volume/network |
| 18 | compose |
| 19 | multi-stage/registry |
| 20 | ilovani konteynerlash |

Bugun **hammasi birga**.

---

## 🏗️ Bugungi stack
```yaml
services:
  web:                 # bizning ilova (build)
    build: .
    ports:
      - "8091:8080"
    depends_on:
      - cache
  cache:               # redis (tayyor image)
    image: redis:alpine
    volumes:
      - cachedata:/data
volumes:
  cachedata:
```
- **web** — Day-20 dagi Python ilova (build qilinadi)
- **cache** — redis (tayyor image)
- **volume** — redis ma'lumotи saqlanadi (Day-17)
- **network** — web `cache` ni NOM bilan topadi (compose avtomatik, Day-18)

## Ishga tushir
```
docker compose -p boss up -d --build
curl localhost:8091                       # web javob beradi
docker compose -p boss exec cache redis-cli ping   # cache: PONG
```

---

## ▶️ Endi ishga
```
devops next       # takror → BOSS stack → MUSTAQIL
devops verify
```
Hammasi tugasa — **3-hafta yakunlanadi!** 🎉  So'ng: `devops exam` · `devops interview` · `devops ai`.
