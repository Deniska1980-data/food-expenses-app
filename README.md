# 💸 Food Expenses App / Výdavkový denník („Výdejový deník“)

📌 [Open the app on Streamlit](https://food-expenses-app-p5tts7gtpumedcsdkhdlw4.streamlit.app)

---

## 🇬🇧 English

### 📌 About the project
A simple bilingual **expenses tracker prototype** built with **Streamlit**.  
It helps users **log, analyze and visualize** their daily expenses.  

- Two language versions: **Slovak/Czech** and **English**  
- Currency conversion (**CZK** as base)  
- Categories such as *Food, Transport, Entertainment, Restaurants & Bars, Drugstore*  
- Friendly and playful UI for both children and older users  

### 🛠️ Development notes
This prototype was **tested for functionality** and continuously improved:  
- ✅ Fixed error messages  
- ✅ Added dual-language labels (Slovak + Czech)  
- ✅ Retested the app after every change
- 
### 🖼 Screenshots  
> Note: Screenshots are illustrative / Obrázky sú ilustračné  
<td align="center">SK Slovak / CZ Czech version<br><br>
<img src="screenshot1.JPG" width="400">
</td>
</tr>
</table>

### 🧑‍💻 Example code snippet
```python
import streamlit as st
import pandas as pd
from datetime import date as dt_date

---

### 🚀 How to run locally
1. Clone this repository
git clone https://github.com/Deniska1980-data/food-expenses-app.git
cd food-expenses-app
2. Install requirements
pip install -r requirements.txt
3. Run Streamlit app
streamlit run app.py


### 🇸🇰 Slovenská / CZ Česká verzia
### 📌 O projekte

Jednoduchý dvojjazyčný prototyp na sledovanie výdavkov vytvorený v Streamlite.
Pomáha používateľom zaznamenávať, analyzovať a vizualizovať svoje denné výdavky.

Dve jazykové verzie: slovenská/česká a anglická

Prepočítavanie mien (základná mena CZK)

Kategórie ako Potraviny, Doprava, Zábava, Reštaurácie a bary, Drogérie

Veselé a hravé prostredie vhodné aj pre deti či starších používateľov

### 🛠️ Poznámky k vývoju

Tento prototyp bol testovaný z hľadiska funkčnosti a postupne vylepšovaný:

✅ Doplnila som dvojjazyčné názvy (slovenské{české) + po přepnutí anglická verzia

✅ Opravila som chybové hlášky

✅ Po každej úprave som aplikáciu znovu testovala


## 🖼️ Ukážky

Poznámka: Obrázky sú ilustračné.

### 🧑‍💻 Ukážka kódu
import streamlit as st
import pandas as pd
from datetime import date as dt_date

### 🔮 Planned features / Plánované funkcie
Automatic exchange rates update from Czech National Bank (ČNB) API
(currently fixed prototype rates:
• 25 CZK = 1 EUR
• 20 CZK = 1 USD
• 30 CZK = 1 GBP)
More categories and subcategories for expenses
Export to Excel/CSV
Simple charts and visualizations directly in the app

### 🚀 Ako spustiť lokálne
1. Naklonuj si repozitár
git clone https://github.com/Deniska1980-data/food-expenses-app.git
cd food-expenses-app
2. Nainštaluj balíčky
pip install -r requirements.txt
3. Spusti aplikáciu
streamlit run app.py

### 📅 Metadata
Date / Dátum: 09/2025
Author / Autor: Denisa Pitnerová
