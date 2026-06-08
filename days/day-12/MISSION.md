# Day-12 — Tarmoq chuqur: DNS, TLS, HTTP debug (to'liq kun)

### 🎯 Bugungi maqsad
Tarmoqni **chuqur** debug qilish: DNS yozuvlari (A/MX/TXT), TLS sertifikat,
HTTP status kodlari, routing. "Sayt ochilmayapti" muammosini topa olish.

> 📦 **Natija:** dig/openssl/curl bilan tarmoq muammosini bosqichma-bosqich tekshirish.

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (public IP, routing) · 2️⃣ Drill (dig A, http kod, port) ·
3️⃣ Asosiy (MX/TXT yozuv, TLS sertifikat, header) · 4️⃣ Callback (Day-5 dns, Day-4 grep) ·
5️⃣ Mini-loyiha "Network Diagnostics" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. DNS yozuv turlari
| Tur | Nima |
|-----|------|
| **A** | nom → IPv4 |
| **AAAA** | nom → IPv6 |
| **MX** | pochta serveri |
| **TXT** | matn (SPF, tasdiqlash) |
| **CNAME** | taxallus (boshqa nomga) |
```
dig +short github.com A      # IP
dig +short MX gmail.com      # pochta serverlari
dig +short TXT google.com    # TXT yozuvlar
```

### 2. TLS/HTTPS sertifikat
```
echo | openssl s_client -connect github.com:443 -servername github.com 2>/dev/null \
  | openssl x509 -noout -dates    # amal qilish muddati (notBefore/notAfter)
```

### 3. HTTP status kodlari
| Kod | Ma'no |
|-----|-------|
| 2xx | OK (200) |
| 3xx | yo'naltirish (301/302) |
| 4xx | mijoz xatosi (404/403) |
| 5xx | server xatosi (500/502) |
```
curl -s -o /dev/null -w "%{http_code}\n" https://github.com   # faqat kod
curl -sI https://github.com                                    # header'lar
```

### 4. Debug tartibi ("sayt ochilmayapti")
1. DNS bormi? (`dig`) → 2. Port ochiqmi? (`nc -z host 443`) → 3. TLS sog'mi? (`openssl`)
→ 4. HTTP javobi? (`curl -I`) → 5. Routing? (`ip route`)

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
