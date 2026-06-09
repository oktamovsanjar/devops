# Day-16 — Dockerfile: o'z image'ingni qur (to'liq kun)

### 🎯 Bugungi maqsad
**Dockerfile** yozib, o'zingning image'ingni **qurish** (`docker build`). Ilovangizni
konteynerga aylantirishning birinchi qadami.

> 📦 **Natija:** Dockerfile yozish, image qurish, tag qo'yish, ishga tushirish.

> 💡 Tez bo'lishi uchun kichik `alpine` asosida quramiz (internet/apt'siz).

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (Dockerfile, build) · 2️⃣ Drill (RUN, COPY, WORKDIR) ·
3️⃣ Asosiy (build+run, COPY app, ENV/EXPOSE, tag) · 4️⃣ Callback (Day-8 skript, Day-1 tuzilma) ·
5️⃣ Mini-loyiha "Custom image" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Dockerfile — image retsepti
```dockerfile
FROM alpine               # asos image
WORKDIR /app              # ishchi papka (ichida)
COPY app.sh /app/app.sh   # hostdan image'ga fayl nusxala
RUN chmod +x app.sh       # qurish vaqtidagi buyruq
EXPOSE 8080               # qaysi port ochiq (hujjat)
ENV NAME=devops           # muhit o'zgaruvchisi
CMD ["sh", "app.sh"]      # container ishga tushganda bajariladigan buyruq
```

### 2. Asosiy direktivalar
| Direktiva | Vazifa |
|-----------|--------|
| `FROM` | asos image (har Dockerfile shundan boshlanadi) |
| `RUN` | **qurish** vaqtida buyruq (paket o'rnatish v.h.) |
| `COPY` | host faylini image'ga ko'chirish |
| `WORKDIR` | ishchi papkani belgilash |
| `ENV` | muhit o'zgaruvchisi |
| `EXPOSE` | port hujjati |
| `CMD` | container **ishga tushganda** bajariladigan asosiy buyruq |

### 3. Qurish va ishga tushirish
```
docker build -t myapp .          # joriy papkadagi Dockerfile'dan image qur (tag: myapp)
docker build -t myapp:1.0 .      # versiya (tag) bilan
docker images                    # qurilgan image ko'rinadi
docker run --rm myapp            # o'z image'ingni ishga tushir
```

### 4. RUN vs CMD (chalkashma!)
- **RUN** — image QURILAYOTGANда bajariladi (natija image'ga "pishadi").
- **CMD** — container ISHGA TUSHGANда bajariladi (har run'da).

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
