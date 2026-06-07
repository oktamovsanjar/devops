# Cheat-sheet: grep

# grep Cheat-Sheet

## Asosiy qidiruv | Basic Search
```
grep "pattern" file.txt          — faylda naqsh qidirish
grep "pattern" *.txt             — barcha .txt fayllardan qidirish
grep "pattern" file1 file2       — bir nechta fayldan qidirish
cat file.txt | grep "pattern"    — pipe orqali qidirish
```

## Katta-Kichik Harf | Case
```
grep -i "pattern" file.txt       — harflar registrini e'tiborsiz qoldirish
grep -iw "word" file.txt         — registrsiz to'liq so'z qidirish
```

## Teskari va To'liq Mos | Invert & Exact
```
grep -v "pattern" file.txt       — mos kelmaganlarni ko'rsatish
grep -w "word" file.txt          — faqat to'liq so'z (word boundary)
grep -x "exact line" file.txt    — faqat to'liq qator mos kelsa
```

## Chiqish Formati | Output
```
grep -n "pattern" file.txt       — qator raqamlari bilan
grep -c "pattern" file.txt       — faqat mos qatorlar sonini
grep -l "pattern" *.txt          — faqat fayl nomlarini
grep -L "pattern" *.txt          — mos kelmagan fayl nomlarini
grep -o "pattern" file.txt       — faqat mos kelgan qismni
grep -h "pattern" *.txt          — fayl nomi ko'rsatmasdan
```

## Kontekst | Context Lines
```
grep -A 3 "pattern" file.txt     — mos qatordan keyin 3 qator
grep -B 3 "pattern" file.txt     — mos qatordan oldin 3 qator
grep -C 3 "pattern" file.txt     — atrofida 3 qator (before + after)
```

## Rekursiv | Recursive
```
grep -r "pattern" /path/         — papkani rekursiv qidirish
grep -r "pattern" .              — joriy papkadan rekursiv
grep -rl "pattern" .             — faqat fayl nomlarini rekursiv
grep -ri "pattern" .             — rekursiv + registrsiz
grep -r --include="*.py" "def" . — faqat .py fayllarda rekursiv
grep -r --exclude="*.log" "err" .— .log fayllarni o'tkazib yuborish
```

## Muntazam Ifodalar | Regex
```
grep "^pattern" file.txt         — qator boshi
grep "pattern$" file.txt         — qator oxiri
grep "^$" file.txt               — bo'sh qatorlar
grep "p.ttern" file.txt          — . — istalgan bitta belgi
grep "colou*r" file.txt          — u — 0 yoki ko'p marta
grep "colou\?r" file.txt         — u — ixtiyoriy (0 yoki 1)
grep "[aeiou]" file.txt          — belgilar to'plami
grep "[^aeiou]" file.txt         — to'plamdan tashqari
grep "[0-9]" file.txt            — raqamlar oralig'i
```

## Kengaytirilgan Regex | Extended Regex (-E / egrep)
```
grep -E "cat|dog" file.txt       — cat YOKI dog
grep -E "colou?r" file.txt       — u — ixtiyoriy
grep -E "go{2,4}gle" file.txt    — g — 2 dan 4 gacha
grep -E "(error|warn)" file.txt  — guruhlash
grep -E "\d+" file.txt           — bir yoki ko'p raqam
```

## Perl Regex | Perl-Compatible (-P)
```
grep -P "\d{3}-\d{4}" file.txt   — telefon naqshi
grep -P "\bword\b" file.txt      — so'z chegarasi
grep -P "(?i)pattern" file.txt   — inline registrsiz
grep -P "\s+" file.txt           — bo'sh joy(lar)
```

## Tizim Log va Amaliy | Practical System
```
grep "error" /var/log/syslog     — tizim logidan xatolik
grep -i "fail" /var/log/auth.log — autentifikatsiya log
grep "WARN\|ERROR" app.log       — WARN yoki ERROR
grep -v "^
