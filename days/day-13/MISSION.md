# Day-13 — Nginx: reverse proxy, TLS (to'liq kun)

### 🎯 Bugungi maqsad
**Nginx** bilan saytni internetga chiqarish: static fayllar, **reverse proxy**
(ilovaga yo'naltirish), **TLS** (HTTPS). Web infratuzilmaning yuragi.

> 📦 **Natija:** to'g'ri nginx config yoza olish — static, reverse proxy, TLS, redirect.

> 💡 Bugun nginx'ni O'RNATMAYMIZ — config FAYLLARini yozasan va tekshiramiz
> (real serverда aynan shu fayllar ishlatiladi). `sudo apt install nginx` keyin o'zing qilasan.

---

## 🗓️ Bugungi kun rejasi (6 blok)
1️⃣ Yo'naltirish (struktura, listen) · 2️⃣ Drill (server_name, root, location) ·
3️⃣ Asosiy (static sayt, reverse proxy, TLS, redirect) · 4️⃣ Callback (Day-12 port, Day-8 skript) ·
5️⃣ Mini-loyiha "Site behind nginx" · 6️⃣ Yakuniy + exam.

---

## 📚 Nazariya

### 1. Nginx nima?
Tez web-server + **reverse proxy**. Tashqaridan so'rovni qabul qilib:
- static fayl bersa — **web server**
- orqadagi ilovaga (Node/Python) uzatsa — **reverse proxy**

### 2. server bloki (static sayt)
```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;
}
```

### 3. Reverse proxy (ilovaga yo'naltirish)
```nginx
server {
    listen 80;
    server_name api.example.com;
    location / {
        proxy_pass http://localhost:3000;   # orqadagi ilova
        proxy_set_header Host $host;
    }
}
```

### 4. TLS (HTTPS) + redirect
```nginx
server {
    listen 443 ssl;
    server_name example.com;
    ssl_certificate     /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    root /var/www/html;
}
server {                       # 80 → 443 yo'naltirish
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

### 5. Sinash
```
nginx -t                 # config sintaksisini tekshir (xato bo'lsa aytadi)
sudo systemctl reload nginx
```

---

## ▶️ Endi ishga
```
devops next
devops verify
```
Kun tugagach:  `devops exam`.
