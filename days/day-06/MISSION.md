# Day-06 — Bash skripting I

### 🎯 Bugungi maqsad
Birinchi **avtomatlashtirish skriptlari**ni yozish: o'zgaruvchi, shart, sikl,
funksiya. DevOps = avtomatlashtirish, avtomatlashtirish = bash.

> 📦 **Natija:** kichik, ishlaydigan skriptlar yoza olish.

---

## 📚 Nazariya (topshiriqlar `devops next`да)

### 1. Skript tuzilishi
```bash
#!/bin/bash          # shebang — qaysi interpretator
name="agent"         # o'zgaruvchi (= atrofida probel YO'Q)
echo "Salom, $name"  # ishlatish: $name
```

### 2. O'zgaruvchilar
```bash
x=5
echo "$x"            # 5  (qo'shtirnoq — xavfsiz)
files=$(ls | wc -l)  # buyruq natijasini olish
```

### 3. Shart (if)
```bash
if [ -f fayl ]; then
    echo "bor"
elif [ "$x" -gt 10 ]; then
    echo "katta"
else
    echo "yo'q"
fi
```
Testlar: `-f` fayl · `-d` papka · `-z` bo'sh · `-eq/-gt/-lt` sonlar · `=` matn.

### 4. Sikl (for / while)
```bash
for i in 1 2 3; do echo $i; done
for f in *.txt; do echo $f; done
while read line; do echo "$line"; done < fayl
```

### 5. Funksiya
```bash
greet() {
    echo "Salom, $1"   # $1 = birinchi argument
}
greet "agent"
```

### 6. Arifmetika
```bash
echo $(( 3 + 4 ))    # 7
echo $(( $1 * $1 ))  # argumentning kvadrati
```

---

## ▶️ Endi ishga
```
devops next       # nima qilishni aytadi
devops verify     # tekshiradi → keyingisi
```
