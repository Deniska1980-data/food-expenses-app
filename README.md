# 🧾 Food Expenses App / Výdavkový denník

Bilingual expenses app (CZK base currency, CNB daily rates) built with **Streamlit**.  
Plne funkčná aplikácia na správu výdavkov s podporou viacerých mien, grafmi a exportom dát.  

👉 [**Spustiť aplikáciu online**](https://food-expenses-app-phgvzfp3bej2cnnnujlmvm.streamlit.app/)  

📱 QR kód pre rýchle spustenie:  
![QR kód](food_expenses_app_qr.png)

---

## ✨ Funkcie
- **Bilingválna aplikácia (čeština / angličtina)**  
- **Podpora viacerých mien** – automatický prepočet na CZK podľa denných kurzov ČNB  
- **Fallback mechanizmus** – ak kurz nie je dostupný, použije sa posledný známy  
- **Kategórie s ikonami / piktogramami** (potraviny, doprava, drogérie, reštaurácie & bary, zdravie, zábava…)  
- **Prehľadné tabuľky** všetkých nákupov s detailami (dátum, krajina, mena, kurz, kategória, poznámka)  
- **Grafy výdavkov podľa kategórií**  
- **Export do CSV** pre ďalšiu analýzu  

---

## 🖼 Screenshoty
### CZ verzia
![CZ verzia](screenshot_CZK_nova_appka.JPG)

### EN verzia
![EN verzia](screenshot_ENG_nova_appka.JPG)

---

## 🚀 Použité technológie
- Python  
- Streamlit  
- Pandas  
- Requests (API – denné kurzy ČNB)  

---

## 📌 Aktuálny stav
✅ Funkčná aplikácia – testovaná na viacerých zariadeniach (Huawei, Samsung, iPhone, Lenovo notebook)  
✅ Testované aj mimo ČR (Slovensko, Nemecko)  
✅ Stabilný prepočet mien + grafy + export  

🔜 **Ďalší krok:** vizuálna úprava (grafika vo forme "výťahu" pre kategórie a meny)  

---

## ⚖️ Licencia
Tento projekt je publikovaný pod licenciou **MIT**.  
Viď [LICENCE](LICENCE).  

---

👩‍💻 Autor: **Denisa Pitnerová (2025)**  
