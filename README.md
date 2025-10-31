# Food Expenses App / Výdavkový denník - prototyp

Bilingual expenses app (CZK base currency, CNB daily rates) built with **Streamlit**.  
Plne funkčná aplikácia na správu výdavkov s podporou viacerých mien, grafmi a exportom dát, ale stále prosím ide iba o testovací prototyp.   

👉 Apkikacia zde: https://food-expenses-app-s4vpaxhrqfmmseggvxxb7t.streamlit.app/

---

## Funkcie
- Bilingválna aplikácia (čeština / angličtina)  
- Podpora viacerých mien – automatický prepočet na CZK podľa denných kurzov ČNB  
- Fallback mechanizmus – ak kurz nie je dostupný, použije sa posledný známy  
- Kategórie s ikonami / piktogramami (potraviny, doprava, drogérie, reštaurácie & bary, zdravie, zábava…)  
- Prehľadné tabuľky všetkých nákupov s detailami (dátum, krajina, mena, kurz, kategória, poznámka)  
- Grafy výdavkov podľa kategórií  
- Export do CSV pre ďalšiu analýzu  

---

## Screenshoty
### CZ verzia
<img src="screenshot_CZK_nova_appka.JPG" alt="CZ verzia" width="400"/>

### EN verzia
<img src="screenshot_ENG_nova_appka.JPG" alt="EN verzia" width="400"/>

---

## Aktuálny stav
- ✅ Funkčná aplikácia – testovaná na viacerých zariadeniach (Huawei, Samsung, iPhone, Lenovo notebook)  
- ✅ Testované aj mimo ČR (Slovensko, Nemecko)  
- ✅ Stabilný prepočet mien + grafy + export  

- 🚧 UX/UI dizajn – vo vývoji (plánovaný originálny vizuál vo forme *„výťahu“*)  

---

## Verzie aplikácie
- **CNB_test_app.py** – hlavná a aktuálna verzia (bilingválna, API ČNB, grafy, kategórie, export, plne funkčná ✅)  
- **app.py a ENG_app.py** – staršie verzie (prototypy bez plnej funkcionality, ponechané pre dokumentáciu vývoja)
  
📄 Published on Kaggle: My Journey with Lightweight RAG in UX/UI
https://www.kaggle.com/code/denisapitnerov/my-journey-with-lightweight-rag-in-ux-ui
---

## Testovanie a vývoj
Aplikácia prešla viacerými fázami vývoja, testovania a ladenia:  

### Testované prostredia
- **Zariadenia:** Huawei, Samsung, iPhone, Lenovo notebook  
- **Krajiny:** Česko, Slovensko, Nemecko  
- **Čas:** testy v rôznych časoch počas dňa, aby sa overilo správanie API  

### Problémy počas vývoja
- ❌ **Chyby pri sťahovaní kurzov z API ČNB** – nie vždy bol kurz dostupný pre vybraný dátum  
- ❌ **Nefunkčný graf** v prvej verzii – vizualizácia padala pri prázdnych dátach  
- ❌ **Dvojjazyčnosť** – prvé verzie miešali CZ a EN dáta v jednej tabuľke  
- ❌ **Export dát** – bolo potrebné nastaviť správne formáty pre CSV/Excel  
- ❌ **Chyby v kóde** – napríklad knižnica *matplotlib* nefunguje v Streamlite, alebo chýbajúce `)` a `"`  

### Riešenia
- ✅ Implementovaný **fallback mechanizmus** – ak nie je kurz k dátumu, použije sa posledný známy  
- ✅ Graf bol opravený a prispôsobený tak, aby zvládal aj prázdne dataset-y  
- ✅ Pridaná logika na **oddelenie jazykových verzií** (CZ/EN)  
- ✅ Implementovaný **export do CSV** cez pandas  
- ✅ Chyby v kóde riešené postupným ladením – kontrola riadkov, odstránenie nefunkčných knižníc (napr. matplotlib tooltip), oprava syntax chýb  

### Práca s AI
Pri písaní kódu som využívala **AI ako pomocníka** (ChatGPT) – na návrh častí kódu alebo štruktúry.  
Ale ja som bola tá, kto musel:  
- testovať aplikáciu v Streamlite,  
- identifikovať chyby a upozorniť AI („aha, tu je chyba, matplotlib tooltip tu nefunguje, odstráň ho“),  
- opravovať jednoduché chyby ako chýbajúce `)` alebo `"`,  
- hľadať API dokumentáciu ČNB,  
- spúšťať appku znova a znova a postupne ju ladiť.  

👉 AI bol pomocník, ale všetko som musela **navrhnúť, otestovať, skontrolovať a dotiahnuť sama**.  

---

## Použité technológie
- Python  
- Streamlit  
- Pandas  
- Requests (API – denné kurzy ČNB)  

---

## Využité znalosti a kurzy
Táto aplikácia je výsledkom kombinácie mojej práce a poznatkov z kurzov:  

- **Python for Everybody (University of Michigan, Coursera)** – zvládnutie základov a pokročilejších techník Pythonu, práca s dátami, API a regulárnymi výrazmi.  
- **DaPython (PyLadies)** – praktické cvičenia a projekty v Pythone, vrátane práce s pandas a vizualizáciami.  
- **UX/UI Design (California Institute of the Arts, Coursera)** – návrh užívateľského rozhrania, prístupnosť, vizuálne prvky a tvorba intuitívnych dizajnov.  
- **Generative AI Data Analyst Specialization (Vanderbilt University)** – využitie AI v dátovej analytike, prompt engineering a efektívna práca s nástrojmi ako ChatGPT.  

---

## Testing and Development (English Summary)
The app went through several iterations of **testing and debugging**:  

- Tested on multiple devices (Huawei, Samsung, iPhone, Lenovo notebook)  
- Tested by users in different countries (CZ, SK, DE)  
- Real-world issues: CNB API not always available, chart crashing with empty datasets, mixed CZ/EN data, CSV export issues, syntax errors in Python code  

### Solutions
- Implemented **fallback mechanism** for missing CNB rates  
- Fixed chart rendering and language separation  
- Added CSV export  
- Debugged Python syntax issues (`)` and `"`)  

### Working with AI
I used **AI (ChatGPT)** as a coding assistant.  
However, I was the one who:  
- tested the app in Streamlit,  
- identified errors and told AI what to fix,  
- removed non-working parts (e.g., matplotlib tooltip in Streamlit),  
- searched CNB API docs,  
- deployed and re-tested until the app was fully functional.  

👉 AI was just a helper – I designed, tested, debugged and delivered the **final working app** myself.  

---

## Licencia
Tento projekt je publikovaný pod licenciou **MIT**.  
Viď [LICENCE](LICENCE).  

---

👩‍💻 Autor: **Denisa Pitnerová (2025)**
