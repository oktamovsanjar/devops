# 📋 PLAN — 8 Haftalik DevOps Yo'l Xaritasi

> Falsafa: **OS → avtomatlashtirish → konteyner → quvur (pipeline) → orkestratsiya
> → infratuzilma kodi → ko'rinuvchanlik (observability) → CAPSTONE.**
> Har bir blok oldingisining ustiga quriladi. Hech qanday "sehr" qoldirilmaydi —
> har bir narsani NEGA ekanini tushunasan.

Har hafta = 6 o'quv kuni + 1 review/dam kuni. Jami ~56 mission.

---

## 🐧 1-HAFTA — Linux & Shell (POYDEVOR)
> DevOpsда hamma narsa OS ustida turadi. Bu haftani mukammal egallasang, qolgani osonlashadi.

| Day | Mavzu |
|----|-------|
| 01 | Fayl tizimi, navigatsiya, yo'llar (FHS), `man`/help — *yer xaritasi* |
| 02 | Ruxsatlar (permissions), egalik (owner/group), `sudo`, `chmod`/`chown` |
| 03 | Jarayonlar (processes), signallar, `systemd` servislar, `journald` loglar |
| 04 | Paket boshqaruvi (`apt`), matn qayta ishlash: `grep`, `sed`, `awk`, pipe |
| 05 | OS darajasida tarmoq: `ip`, `ss`, DNS, `/etc/hosts`, `ssh`, `curl` |
| 06 | Bash skripting I: o'zgaruvchilar, shartlar, sikllar, funksiyalar, exit code |
| 07 | 🔁 Review + **1-hafta BOSS** + dam |

## 🔧 2-HAFTA — Bash, Git, Tarmoq (AVTOMATLASHTIRISH)
| Day | Mavzu |
|----|-------|
| 08 | Bash II: argumentlar, `getopts`, xato boshqaruvi, `trap`, real skriptlar |
| 09 | `cron`, rejalashtirilgan ishlar, log rotation, maintenance skriptlari |
| 10 | Git asoslari: `init`, `commit`, branch, merge, rebase, `.gitignore` |
| 11 | Git jamoa: remote, GitHub, Pull Request, conflict yechish, workflow |
| 12 | Tarmoq chuqur: TCP/IP, portlar, TLS, HTTP/HTTPS, DNS yozuvlari, debugging |
| 13 | `nginx`: reverse proxy, web server, TLS sertifikat |
| 14 | 🔁 Review + **2-hafta BOSS** (nginx orqasida sayt + deploy skript + git) |

## 📦 3-HAFTA — Docker / Konteynerlar
| Day | Mavzu |
|----|-------|
| 15 | Konteyner tushunchasi, namespace/cgroup, `docker run`, image vs container |
| 16 | `Dockerfile`, image qurish, layerlar, cache, best practices |
| 17 | Volume, network, env, port, log, konteyner debug |
| 18 | Docker Compose (ko'p konteynerli ilova) |
| 19 | Multi-stage build, image optimizatsiya, registry (GHCR), security scan |
| 20 | Real ilovani to'liq konteynerlash (API + DB) |
| 21 | 🔁 Review + **3-hafta BOSS** |

## 🚀 4-HAFTA — CI/CD (GitHub Actions)
| Day | Mavzu |
|----|-------|
| 22 | CI/CD falsafasi, GitHub Actions asoslari (workflow, job, step, trigger) |
| 23 | Build + test quvuri (pipeline) |
| 24 | CI'da Docker image qurish va GHCR'ga push |
| 25 | Secrets, environments, matrix build, cache |
| 26 | CD: avtomatik deploy (serverga SSH orqali) |
| 27 | To'liq CI/CD loyihasi |
| 28 | 🔁 Review + **4-hafta BOSS** |

## ☸️ 5-HAFTA — Kubernetes I
| Day | Mavzu |
|----|-------|
| 29 | K8s arxitektura (control plane, node, etcd, kubelet), `kind`+`kubectl` o'rnatish |
| 30 | Pod, ReplicaSet, Deployment |
| 31 | Service, k8s tarmog'i, ichki DNS |
| 32 | ConfigMap, Secret, env, volume |
| 33 | Ingress, ilovani tashqariga ochish |
| 34 | Konteynerlangan ilovani `kind` klasterga deploy qilish |
| 35 | 🔁 Review + **5-hafta BOSS** |

## ⎈ 6-HAFTA — Kubernetes II + Helm
| Day | Mavzu |
|----|-------|
| 36 | Probes (liveness/readiness), resource requests/limits |
| 37 | Namespace, RBAC asoslari, ServiceAccount |
| 38 | StatefulSet, PersistentVolume, storage |
| 39 | Helm: chart, templating, values, release |
| 40 | Ilovani Helm chart sifatida paketlash |
| 41 | CI/CD → k8s'ga avtomatik deploy (GitOps kirish) |
| 42 | 🔁 Review + **6-hafta BOSS** |

## 🏗️ 7-HAFTA — IaC (Terraform) + Config (Ansible) + Cloud (AWS)
| Day | Mavzu |
|----|-------|
| 43 | AWS asoslari: IAM, EC2, S3, VPC, region (+ xarajat xavfsizligi) |
| 44 | Terraform asoslari: provider, resource, state, `plan`/`apply` |
| 45 | Terraform: variable, output, module; real resurs yaratish |
| 46 | Terraform state boshqaruvi, remote backend |
| 47 | Ansible asoslari: inventory, playbook, module, idempotency |
| 48 | Ansible role, serverni Ansible bilan sozlash |
| 49 | 🔁 Review + **7-hafta BOSS** |

## 📡 8-HAFTA — Observability + CAPSTONE
| Day | Mavzu |
|----|-------|
| 50 | Monitoring falsafasi, Prometheus (o'rnatish, scrape, PromQL) |
| 51 | Grafana (dashboard, datasource, vizualizatsiya) |
| 52 | Alerting: Alertmanager → **Telegram**! + SLO/SLI (SRE'ga ko'prik) |
| 53 | Logging: markazlashtirilgan loglar (Loki konsepti) |
| 54-56 | 🏆 **CAPSTONE:** ilova → Git → CI/CD → Docker → k8s → Terraform → Prometheus/Grafana → Telegram alert |
| Final | Portfolio jilolash, rezyume, intervyu savollari (mock interview) |

---

## 🎯 Bootcamp oxirida sen bilasan:
- Linux'ni ichidan, ishonch bilan boshqarishni
- Bash bilan ishlarni avtomatlashtirishni
- Git/GitHub'da professional ishlashni
- Ilovalarni konteynerlash va Docker'ni
- CI/CD quvurlari qurishni (GitHub Actions)
- Kubernetes'da ilova ishga tushirish va boshqarishni
- Terraform bilan infratuzilmani kod sifatida yozishni
- Ansible bilan serverlarni sozlashni
- Prometheus + Grafana bilan tizimni kuzatishni
- **Va eng muhimi:** muammoni mustaqil debug qilishni

> Bu — haqiqiy **Junior DevOps Engineer** to'plami. Capstone — portfoliongdagi 1-loyiha.
