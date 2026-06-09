# Day-19 — Optimizatsiya & registry (to'liq kun)

### 🎯 Bugungi maqsad
Image'ni **kichik va xavfsiz** qilish (multi-stage build, .dockerignore) va uni
**registry**ga joylash (push/pull). Real ishlab chiqarish ko'nikmasi.

> 📦 **Natija:** multi-stage bilan kichik image + lokal registry'ga push/pull.

> 🧗 **Bugungi narvon:** 📖 nazariya → 🛠️ qadamli amaliy → 🎯 mustaqil (qadamsiz) →
> 🧠 quiz → 🎓 exam → 🎤 interview → 💬 ai-suhbat.

---

## 📚 Nazariya

### 1. Muammo: image katta bo'lib ketadi
Build vositalari (compiler, npm, ...) yakuniy image'ga kerak emas, lekin qoladi → katta, sekin, xavfli.

### 2. Multi-stage build — yechim
```dockerfile
FROM golang AS build           # 1-bosqich: quramiz (og'ir)
WORKDIR /src
COPY . .
RUN go build -o app .

FROM alpine                    # 2-bosqich: faqat natija (yengil)
COPY --from=build /src/app /app
CMD ["/app"]
```
> Yakuniy image'да faqat `app` — compiler yo'q. Kichik!

### 3. .dockerignore — build kontekstini kichraytirish
```
node_modules
.git
*.log
```
> Keraksiz fayllar build'ga yuborilmaydi → tez, kichik, xavfsiz.

### 4. Registry — image'lar ombori
```
docker tag myapp localhost:5000/myapp     # registry uchun nomlash
docker push localhost:5000/myapp          # joylash
docker pull localhost:5000/myapp          # boshqa joydan olish
```
> Docker Hub, GHCR, yoki o'zingning registry'ng (`registry:2` image bilan lokal).

### 5. Image hajmi va tarixi
```
docker images                  # hajm (SIZE ustuni)
docker history myapp           # qatlamlar va hajmi
```

---

## ▶️ Endi ishga (to'liq narvon)
```
devops next       # blokма-blok: nazariy → amaliy → MUSTAQIL
devops verify     # tekshiradi → keyingisi
```
Kun tugagach:
```
devops exam            # 🎓 hintsiz imtihon
devops interview       # 🎤 AI mock-intervyu (kredit bo'lsa)
devops ai "..."        # 💬 ustoz bilan suhbat (kredit bo'lsa)
```
