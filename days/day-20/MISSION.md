# Day-20 — Real ilovani konteynerlash (to'liq kun)

### 🎯 Bugungi maqsad
Haqiqiy **web-ilovani** (Python) to'liq konteynerlash: kod → Dockerfile → build →
run → compose → registry. 15-19 ko'nikmalarini **bitta real ishда** birlashtirasan.

> 📦 **Natija:** ishlaydigan konteynerlangan ilova + compose + registry'ga joylash.

> 🧗 Narvon: 📖 nazariya → 🛠️ qadamli → 🎯 mustaqil → 🧠 quiz → 🎓 exam → 🎤 interview → 💬 suhbat.

---

## 📚 Bu hafta nimani o'rganding (qisqa)
| Day | Ko'nikma |
|-----|----------|
| 15 | run/ps/logs/exec |
| 16 | Dockerfile (build) |
| 17 | volume/network |
| 18 | compose |
| 19 | multi-stage/registry |

Bugun shularning **hammasini** bitta ilovaga qo'llaysan.

---

## 🏗️ Bugungi ilova: kichik Python web-server
```python
# app.py
from http.server import BaseHTTPRequestHandler, HTTPServer
print("App ishga tushdi", flush=True)
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Salom konteynerdan!\n")
HTTPServer(("0.0.0.0", 8080), H).serve_forever()
```

## Dockerfile
```dockerfile
FROM python:3-alpine
WORKDIR /app
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]
```

## Oqim
```
docker build -t myapp .            # 1. image qur (Day-16)
docker run -d -p 8090:8080 myapp   # 2. ishga tushir (host 8090 -> ichki 8080)
curl localhost:8090                # 3. tekshir -> "Salom konteynerdan!"
docker compose up -d               # 4. compose bilan (Day-18)
docker push localhost:5000/myapp   # 5. registry'ga (Day-19)
```

---

## ▶️ Endi ishga
```
devops next       # nazariy → qadamli → MUSTAQIL
devops verify
```
Kun tugagach:  `devops exam` · `devops interview` · `devops ai "..."`.
