# 📊 SaaS J-Görbe esetére ÁR és SZÜKSÉGES BEFEKTETÉS kalkulátor

Egy interaktív Streamlit olyan startupok számára, amelyek fejlődése siker esetén J-görbét ír le.
Segít eladási árat (előfizetési díjat) és szükséges alaptőkét meghatározni, az alábbi tényezők változtatgatásával:


* a Product-Market Fit (PMF) hónapja,
* a virális növekedést (K-faktor),
* a CAC (Customer Acquisition Cost) alakulását,
* lehullási (felhasználó vesztési) arány.
Az eszköz azt is megmutatja, hogy a startup mikor megy csődbe vagy válik nyereségessé.

Az alkalmazás csúszkákkal állítható paramétereket használ, így valós időben vizsgálható különböző üzleti modellek túlélési esélye.

---

# 🚀 Funkciók

## 📈 Interaktív pénzügyi szimuláció

A felhasználó állíthatja:

* indulótőkét,
* havi előfizetési díjat,
* ügyfélszerzési költséget (CAC),
* havi fix költségeket,
* churn rátát,
* PMF időpontját,
* fizetett növekedési ütemet.

---

## 🧠 Dinamikus K-faktor modell

A szimulátor egy időfüggő virális terjedési modellt használ:

1. **Pre-PMF szakasz** → alacsony organikus növekedés
2. **PMF áttörés** → gyorsuló virális terjedés
3. **Hipernövekedés** → akár önfenntartó növekedés
4. **Érettségi fázis** → piac telítődése

---

## 📊 Vizualizációk

Az alkalmazás több grafikonon jeleníti meg:

* a K-faktor változását,
* a havi cash-flow görbét,
* a megmaradt tőkét,
* a J-görbe alakulását,
* a csőd vagy túlélés pontját.

---

# 🖼️ Példa felhasználási esetek

* SaaS startup pénzügyi modellezés
* befektetői prezentációk előkészítése
* growth hacking szcenáriók tesztelése
* CAC vs. virális növekedés elemzés
* Product-Market Fit időzítésének vizsgálata
* startup runway kalkuláció

---

# ⚙️ Telepítés

## 1. Repository klónozása

```bash
git clone https://github.com/felhasznalonev/repository-nev.git
cd repository-nev
```

## 2. Függőségek telepítése

```bash
pip install -r requirements.txt
```

## 3. Streamlit alkalmazás indítása

```bash
streamlit run jgorbe3.py
```

---

# 📦 Szükséges csomagok

```txt
streamlit
matplotlib
numpy
```

---

# 🧮 A modell logikája

A szimuláció figyelembe veszi:

* fizetett ügyfélszerzést,
* organikus/virális növekedést,
* churn hatást,
* működési költségeket,
* havi nettó cash-flowt,
* tőkeállomány változását.

A virális növekedést egy dinamikus K-faktor görbe modellezi, amely PMF után gyorsul fel.

---

# 📉 Mit jelent a J-görbe?

A legtöbb startup kezdetben veszteséges:

* magas CAC,
* alacsony bevétel,
* folyamatos tőkeégetés.

Ha sikerül elérni a Product-Market Fit állapotot, a növekedés exponenciálissá válhat, és a vállalkozás kiléphet a veszteséges szakaszból.

A szimulátor ezt a folyamatot teszi vizuálisan elemezhetővé.

---

# 🛠️ Technológiák

* Python
* Streamlit
* Matplotlib
* NumPy

---

# 🎯 Cél

Az alkalmazás célja, hogy:

* szemléletesen bemutassa a startupok növekedési dinamikáját,
* segítsen pénzügyi szcenáriók tesztelésében,
* edukációs és stratégiai eszközként szolgáljon alapítók és befektetők számára.

---

# 📄 Licenc

MIT License

---

# 🤝 Hozzájárulás

Pull requestek és ötletek szívesen fogadottak.

---

# ⭐ Ha tetszik a projekt

Adj egy csillagot a repositorynak ⭐

