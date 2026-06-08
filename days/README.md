# 📂 Kunlar tuzilishi (har kun bir xil)

Har bir `day-XX/` papkasi **bitta standart**ga amal qiladi. Ikki turdagi narsa bor:

```
days/day-XX/
├── MISSION.md     📖 nazariya — o'qiysan (o'zgartirma)
├── tasks.json     📋 bugungi topshiriqlar (o'zgartirma)
├── exam.json      🎓 amaliy imtihon — bo'lsa (o'zgartirma)
├── fixtures/      📦 tayyor namuna fayllar — topshiriq kiruvchisi (o'zgartirma)
├── quest/         🏴 BOSS jumboq materiallari (o'zgartirma)
│
├── work/          ⌨️  >>> SHU YERDA ISHLAYSAN <<<
└── exam/          🎓 imtihon ish-joyi (devops exam o'zi yaratadi)
```

## Qoida — sodda

| Papka | Kim uchun | Sen nima qilasan |
|-------|-----------|------------------|
| `MISSION.md`, `tasks.json`, `fixtures/`, `quest/` | **kurs beradi** | faqat **o'qiysan / ishlatasan** |
| **`work/`** | **sen** | barcha faylni **shu yerда** yaratasan |
| `exam/` | `devops exam` | avtomatik — qo'l tegizma |

## Ishlash tartibi

```bash
devops next               # nima qilishni aytadi + ish-papkani ko'rsatadi
cd ~/devops/days/day-XX/work   # shu yerga o'tib ishla
# ... fayllarni yarat ...
devops verify             # tizim tekshiradi → keyingisiga o'tkazadi
```

## Muhim eslatmalar

- **`work/` yo'qolmaydi va o'chmaydi** — `devops` har safar uni avtomatik tekshirib turadi
  (umumiy qoida: `work/` doim mavjud, hech qachon ichidagi ishing o'chmaydi).
- Topshiriq tekshiruvida ikki o'zgaruvchi ishlatiladi:
  - `$LAB` = `days/day-XX/work` (sening ish-papkang)
  - `$DAY` = `days/day-XX` (kun ildizi — `fixtures/` shu yerда)
- **`work/`, `exam/`, `quest/`** git'ga ketmaydi (`.gitignore`):
  ish-natijalaring shaxsiy, `quest/` esa flag'larni ochib qo'ymaslik uchun yashirin.
- Hamma kun bir xil — kun-2 ham, kun-50 ham aynan shu tuzilishda.
