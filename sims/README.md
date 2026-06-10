# 🚑 sims/ — diagnostika stsenariylari (devops sim)

Har bir papka = bitta **buzilgan tizim** stsenariysi. `devops sim` real buzuq
muhit quradi — o'quvchi alomatni ko'radi, log o'qiydi, sababini topadi va
**rostan tuzatadi**. Bu real ishdagi troubleshooting'ning mashqi.

## sim.json formati
| Maydon | Ma'no |
|--------|-------|
| `id` | papka nomi bilan bir xil slug |
| `topic` | linux/bash/git/networking/docker/... — faqat O'RGANILGAN mavzular ochiladi |
| `min_day` | shu kundan boshlab ochiq (mavzu o'tilgan kun) |
| `difficulty` | 1-3 (⭐) |
| `xp` | to'liq yechim XP'si (har hint −5, minimum 10) |
| `title`, `story[]` | insident hikoyasi |
| `symptom` | o'quvchi KO'RADIGAN alomat (buyruq + natija) |
| `goal` | nima holatga keltirish kerak |
| `setup` | buzuq muhitni quruvchi shell (satr yoki ro'yxat). `$SIM` = lab papka |
| `check` | exit 0 = tuzatilgan (shu yagona haqiqat manbai) |
| `hints[]` | 3 ta progressiv hint (umumiy → aniq) |
| `solution` | yechim tushuntirishi (yechilgach/giveup'da ko'rsatiladi) |
| `cleanup` | jarayon/konteyner qoldiqlarini tozalash (ixtiyoriy) |

## Qoidalar (yangi sim yozishda)
- **Hammasi `$SIM`** (`sims/.lab/<id>/`, gitignored) **ichida buzilsin** — real tizimga tegma.
- Portlar: **8095–8099** oralig'i (host 8080 band!). Docker nomlari: `simfix-*` prefiks.
- Jarayon ochsang — `cleanup`da o'ldir; konteyner/image ochsang — `cleanup`da o'chir.
- `check` aldab bo'lmaydigan bo'lsin (holatni tekshir, faylning borligini emas).
- Har sim QURILGANDA test qilinsin: setup → check FAIL → yechim → check PASS → cleanup.
- Hint narvoni: 1-hint = qayerga qarashni, 2-hint = sababni, 3-hint = buyruqni beradi.

## Hozirgi qamrov (1–3-hafta)
linux 4 · bash 2 · git 2 · networking 2 · docker 4 — jami **14 stsenariy**.
Keyingi haftalar (cicd/k8s/terraform) o'z simlari bilan keladi.
