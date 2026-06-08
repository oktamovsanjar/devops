# Day-05 — Tarmoq asoslari

### 🎯 Bugungi maqsad
Serverning **tarmog'ini** tushunish: IP, portlar, DNS, va `curl` bilan so'rov yuborish.
"Sayt ochilmayapti" muammosini diagnoz qila olish.

> 📦 **Natija:** port/ulanish/DNS muammosini topish ko'nikmasi.

---

## 📚 Nazariya (topshiriqlar `devops next`да)

### 1. IP manzil
```
hostname -I        # serverning IP(lar)i
ip a               # barcha interfeyslar
```
`127.0.0.1` = localhost (o'zim). `0.0.0.0` = barcha interfeys.

### 2. Portlar (ss)
```
ss -tlnp           # tinglanayotgan TCP portlar + jarayon
ss -tlnp | grep 80 # 80-portni kim egallagan
```
Standart portlar: **80** HTTP · **443** HTTPS · **22** SSH · **53** DNS.

### 3. DNS (nom → IP)
```
getent hosts google.com   # tez tarjima
nslookup google.com
dig google.com
```

### 4. curl — HTTP so'rov
```
curl https://api.test            # javob tanasini ol
curl -s https://api.test         # jim (progress yo'q)
curl -sI https://github.com      # faqat header (HTTP status)
```
HTTP status: **200** OK · **301** redirect · **404** topilmadi · **500** server xatosi.

### 5. ssh — masofaviy ulanish
```
ssh user@host            # serverga kirish
scp fayl user@host:/yo'l # fayl nusxalash (SSH ustidan)
```

### 6. TCP vs UDP
- **TCP** — ulanishli, ishonchli (web, ssh).
- **UDP** — ulanishsiz, tez, kafolatsiz (DNS, video).

---

## ▶️ Endi ishga
```
devops next       # nima qilishni aytadi
devops verify     # tekshiradi → keyingisi
```
