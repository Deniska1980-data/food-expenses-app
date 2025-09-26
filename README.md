# 💸 Food Expenses App / Výdavkový denník („Výdejový deník“)

[👉 Open the app on Streamlit](https://food-expenses-app-p5tts7gtpumedcsdkhdlw4.streamlit.app/)

---

## 🇬🇧 English

### 📌 About the project
A simple bilingual **expenses tracker prototype** built with Streamlit.  
It helps users **log, analyze and visualize their daily expenses**.  

- Two language versions: **Slovak/Czech** and **English**  
- Currency conversion (CZK as base)  
- Categories such as Food, Transport, Entertainment, Restaurants & Bars, Drugstore  
- Friendly UI for both children and older users  

This prototype was **tested for functionality**, improved with:  
✔️ Dual-language labels (Slovak + Czech)  
✔️ Fixed error messages  
✔️ Retested after each improvement  

---

### 🖼️ Screenshots
*Note: Screenshots are illustrative / Obrázky sú ilustračné  

<table>
<tr>
<td align="center">🇸🇰🇨🇿 Slovak / Czech version<br><br>
<img src="screenshot1.JPG" width="400">
</td>

---

### 🧑‍💻 Example code snippet
```python
import streamlit as st
import pandas as pd
from datetime import date as dt_date

### 🚀 How to run locally
1. Clone this repository
git clone https://github.com/Deniska1980-data/food-expenses-app.git
cd food-expenses-app
2. Install requirements
pip install -r requirements.txt
3. Run Streamlit app
streamlit run app.py

### 🇸🇰🇨🇿 Slovenská / Česká verzia
## 📌 O projekte

Jednoduchý dvojjazyčný prototyp na sledovanie výdavkov vytvorený v Streamlite.
Pomáha používateľom zaznamenávať, analyzovať a vizualizovať svoje denné výdavky.

Dve jazykové verzie: slovenská/česká a anglická

Prepočítavanie mien (základná mena CZK)

Kategórie ako Potraviny, Doprava, Zábava, Reštaurácie a bary, Drogérie

Veselé a hravé prostredie vhodné aj pre deti či starších používateľov

Tento prototyp bol testovaný z hľadiska funkčnosti, postupne bol vylepšovaný:
✔️ Doplnila som dvojjazyčné názvy (slovenské aj české)
✔️ Opravila som chybové hlášky
✔️ Po každej úprave som aplikáciu znovu testovala

## 🖼️ Ukážky

Poznámka: Obrázky sú ilustračné.

### 🧑‍💻 Ukážka kódu
import streamlit as st
import pandas as pd
from datetime import date as dt_date

### 🚀 Ako spustiť lokálne
1. Naklonuj si repozitár
git clone https://github.com/Deniska1980-data/food-expenses-app.git
cd food-expenses-app
2. Nainštaluj balíčky
pip install -r requirements.txt
3. Spusti aplikáciu
streamlit run app.py

### 👩‍💻 Dátum 09/2025, Author: Denisa Pitnerová
