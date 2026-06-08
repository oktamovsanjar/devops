# Day-04 — Paketlar va matn ustasi

### 🎯 Bugungi maqsad
**Matn oqimini boshqarish:** `grep`, `sed`, `awk`, `pipe` (|) bilan minglab qatorli
ma'lumotdan kerakli narsani bir buyruqда sug'urib olish. Va `apt` asoslari.

> 📦 **Natija:** logdan xato/IP/qiymatni filtrlash, almashtirish, hisoblash.

---

## 📚 Nazariya (topshiriqlar `devops next`да)

### 1. Pipe ( | ) — oqimni ulash
Bir buyruq natijasini ikkinchisiga uzatadi:
```
cat access.log | grep ERROR | wc -l
```

### 2. grep — qatorlarni filtrlash
```
grep ERROR fayl        # ERROR bor qatorlar
grep -c ERROR fayl     # SONI
grep -i error fayl     # katta-kichik harfsiz
grep -r TODO .         # papka ichidan rekursiv
grep -v INFO fayl      # INFO BO'LMAGAN qatorlar
```

### 3. awk — ustunlar bilan ishlash
```
awk '{print $1}' fayl       # 1-ustun
awk '{print $1, $3}' fayl   # 1 va 3-ustun
awk '$3 > 500' fayl         # 3-ustun > 500 bo'lgan qatorlar
```

### 4. sed — matnni almashtirish
```
sed 's/eski/yangi/' fayl        # birinchi moslikni almashtir
sed 's/eski/yangi/g' fayl       # har bir moslikni (global)
sed -n '2,5p' fayl              # 2-5 qatorlar
```

### 5. Klassik tahlil zanjiri
```
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head
# ustun -> sarala -> sana -> kattadan kichikka -> top
```

### 6. apt — paketlar
```
sudo apt update              # ro'yxatni yangila
sudo apt install jq          # o'rnat
apt list --installed         # o'rnatilganlar
git --version                # versiya
```

---

## ▶️ Endi ishga
```
devops next       # nima qilishni aytadi
devops verify     # tekshiradi → keyingisi
```
