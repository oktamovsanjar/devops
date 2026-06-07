# 📚 CURRICULUM — To'liq Kunlik Master-Reja (56 kun)

> Bu — butun yo'lning yagona manbai. Har kun aniq **maqsad** va **natija** (deliverable)
> bilan. Roadmap shu rejaga asoslanadi; har kun oldingisiga tayanadi.

## 🧱 Har kunning tuzilishi (bir xil, takrorsiz)
Bitta narsa — bitta joyda. Chalkashlik yo'q:
- **🎯 Brief** — kun maqsadi (1-2 jumla, tasks.json ichida)
- **📚 Theory** — qisqa nazariya, faqat tushuncha (MISSION.md — topshiriq takrorlamaydi)
- **🏗️ Topshiriqlar** — `devops task` (YAGONA manba, avto-tekshiriladi)
- **🧩 Quest** — ba'zi kunlar: jumboq + flag (faqat o'yin fayllarida)
- **✅ Yakun** — `devops done`

---

## 🐧 1-HAFTA — Linux poydevori
> Ko'nikma: navigatsiya · ruxsat · jarayon · matn ishlash · tarmoq · bash

| Day | Mavzu | 🎯 Maqsad | 📦 Natija (deliverable) |
|----|-------|----------|------------------------|
| 1 | Fayl tizimi & navigatsiya | Serverda erkin yurish, fayl topish/o'qish | Tartibli ish maydoni + host hujjati + log triage |
| 2 | Ruxsatlar & egalik | `chmod/chown/sudo` ni tushunish | "Permission denied" ni to'g'ri yechish |
| 3 | Jarayonlar & systemd | Servis va jarayonni boshqarish | O'lik servisni topib qayta tiklash + log o'qish |
| 4 | Paket & matn ustasi | `apt` + `grep/sed/awk/pipe` | Katta logdan kerakli ma'lumotni 1 buyruqda ajratish |
| 5 | Tarmoq asoslari | `ip/ss/dns/ssh/curl` | Port/ulanish muammosini diagnoz qilish |
| 6 | Bash skripting I | O'zgaruvchi/shart/sikl/funksiya | Ishlaydigan kichik avtomatlashtirish skripti |
| 7 | 🏁 1-hafta BOSS | Haftani birlashtirish | Real ssenariy: serverni sozlash + skript |

## 🔧 2-HAFTA — Avtomatlashtirish & versiya nazorati
> Ko'nikma: bash II · cron · **git** · tarmoq chuqur · nginx

| Day | Mavzu | 🎯 Maqsad | 📦 Natija |
|----|-------|----------|----------|
| 8 | Bash skripting II | `getopts/trap/set -e`, xato boshqaruvi | Mustahkam, argumentli skript |
| 9 | Cron & maintenance | Rejalashtirilgan ishlar, log rotation | Avtomatik backup/monitoring skripti (cron) |
| 10 | Git asoslari | `commit/branch/merge/.gitignore` | Loyihani git'ga olish, tarix yuritish |
| 11 | Git jamoa (GitHub) | Remote, PR, conflict yechish | GitHub'ga push + birinchi Pull Request |
| 12 | Tarmoq chuqur | TCP/IP, TLS, HTTP, DNS yozuvlar | Tarmoq muammosini chuqur debug qilish |
| 13 | Nginx | Reverse proxy, TLS sertifikat | Saytni nginx orqasiga qo'yish |
| 14 | 🏁 2-hafta BOSS | Birlashtirish | Sayt + deploy skript + git, hammasi birga |

## 📦 3-HAFTA — Docker
> Ko'nikma: konteyner · Dockerfile · volume/network · compose · registry · **YAML**

| Day | Mavzu | 🎯 Maqsad | 📦 Natija |
|----|-------|----------|----------|
| 15 | Konteyner asoslari (+YAML) | `docker run`, image vs container, YAML | Tayyor image'ni ishga tushirish |
| 16 | Dockerfile | O'z image'ingni qurish | Ilovangiz uchun ishlaydigan Dockerfile |
| 17 | Volume, network, debug | Ma'lumot saqlash, konteyner tarmog'i | Ma'lumot saqlanadigan konteyner + debug |
| 18 | Docker Compose | Ko'p konteynerli ilova | API + DB ni bitta `compose up` bilan |
| 19 | Optimizatsiya & registry | Multi-stage, GHCR, security scan | Kichik, xavfsiz image registry'da |
| 20 | Real ilovani konteynerlash | Hammasini birlashtirish | Konteynerlangan to'liq ilova |
| 21 | 🏁 3-hafta BOSS | Birlashtirish | Compose bilan ishlaydigan multi-servis |

## 🚀 4-HAFTA — CI/CD (GitHub Actions)
| Day | Mavzu | 🎯 Maqsad | 📦 Natija |
|----|-------|----------|----------|
| 22 | GitHub Actions asoslari | Workflow/job/step/trigger | Birinchi yashil (green) CI build |
| 23 | Build + test pipeline | Avtomatik test | Har push'da test ishlaydigan pipeline |
| 24 | CI'da Docker + GHCR | Image qurish va push | CI image'ni avtomatik registry'ga chiqaradi |
| 25 | Secrets & matrix | Maxfiy ma'lumot, ko'p muhit | Xavfsiz, matritsali pipeline |
| 26 | CD — avtomatik deploy | Serverga avtomatik chiqarish | Push → avtomatik deploy |
| 27 | To'liq CI/CD loyihasi | Birlashtirish | Kod → test → image → deploy zanjiri |
| 28 | 🏁 4-hafta BOSS | Birlashtirish | To'liq avtomatik CI/CD quvuri |

## ☸️ 5-HAFTA — Kubernetes I
| Day | Mavzu | 🎯 Maqsad | 📦 Natija |
|----|-------|----------|----------|
| 29 | K8s arxitektura + kind | Tushunchalar, klaster o'rnatish | Ishlaydigan lokal `kind` klaster |
| 30 | Pod & Deployment | Ilovani ishga tushirish | Replikali Deployment |
| 31 | Service & DNS | Tarmoq, ichki ulanish | Pod'larga barqaror ulanish |
| 32 | ConfigMap & Secret | Konfiguratsiya boshqaruvi | Configni koddan ajratish |
| 33 | Ingress | Tashqariga ochish | Domen orqali ilovaga kirish |
| 34 | Ilovani deploy | Birlashtirish | Konteynerlangan ilova klasterda |
| 35 | 🏁 5-hafta BOSS | Birlashtirish | K8s'da ishlaydigan to'liq ilova |

## ⎈ 6-HAFTA — Kubernetes II + Helm
| Day | Mavzu | 🎯 Maqsad | 📦 Natija |
|----|-------|----------|----------|
| 36 | Probes & limitlar | Sog'liq tekshiruvi, resurs | Barqaror, cheklangan Deployment |
| 37 | Namespace & RBAC | Ajratish, xavfsizlik | Rolga asoslangan ruxsatlar |
| 38 | StatefulSet & PV | Ma'lumotli ilovalar | Saqlanuvchi (stateful) ilova |
| 39 | Helm asoslari | Paketlash, template | Helm bilan deploy |
| 40 | Helm chart yaratish | O'z chartingiz | Ilovangiz uchun Helm chart |
| 41 | CI/CD → K8s | GitOps kirish | Push → avtomatik k8s deploy |
| 42 | 🏁 6-hafta BOSS | Birlashtirish | Helm + CI bilan to'liq oqim |

## 🏗️ 7-HAFTA — IaC + Cloud (Terraform/Ansible/AWS)
| Day | Mavzu | 🎯 Maqsad | 📦 Natija |
|----|-------|----------|----------|
| 43 | AWS asoslari | IAM/EC2/S3/VPC, xarajat xavfsizligi | Cloud tushunchasi + xavfsiz IAM |
| 44 | Terraform asoslari | provider/resource/state | Birinchi `terraform apply` |
| 45 | Terraform modullar | Qayta ishlatish, variable/output | Modulli infratuzilma |
| 46 | Terraform state | Remote backend, jamoa | Xavfsiz, jamoaviy state |
| 47 | Ansible asoslari | inventory/playbook/idempotency | Serverni Ansible bilan sozlash |
| 48 | Ansible rollar | Tartibli, qayta ishlatiluvchi | Rolga asoslangan konfiguratsiya |
| 49 | 🏁 7-hafta BOSS | Birlashtirish | Terraform + Ansible bilan to'liq provisioning |

## 📡 8-HAFTA — Observability + CAPSTONE
| Day | Mavzu | 🎯 Maqsad | 📦 Natija |
|----|-------|----------|----------|
| 50 | Prometheus | Metrika yig'ish, PromQL | Ilovani Prometheus kuzatadi |
| 51 | Grafana | Vizualizatsiya | Jonli dashboard |
| 52 | Alerting + SLO/SLI | Ogohlantirish (Telegram!) | Muammoda alert keladi |
| 53 | Logging | Markazlashgan loglar (Loki) | Bir joyda barcha loglar |
| 54 | 🏆 Capstone I | Loyihani qurish | Ilova + Docker + Git |
| 55 | 🏆 Capstone II | Pipeline + K8s | CI/CD + Kubernetes deploy |
| 56 | 🏆 Capstone III | Kuzatuv + portfolio | Monitored, IaC, portfolio tayyor |

---

## 🎓 Yakuniy natija
56 kun oxirida sening **portfolioda**: konteynerlangan ilova → Git → CI/CD →
Kubernetes → Terraform → Prometheus/Grafana monitoring — hammasi bir loyihada.
Bu — haqiqiy **Junior DevOps Engineer** darajasi.
