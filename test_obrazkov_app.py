import streamlit as st
from datetime import datetime
import time
import pandas as pd
import random

# Nastavenie názvu aplikácie
st.set_page_config(page_title="Výdavkový denník", page_icon="🛗")

# Cesta k obrázkom
IMG1 = "vytah_zavrete_dvere_obrazok1.png"
IMG2 = "obrazok_vnutro_vytah_s_appko_obrazok2.JPG"
IMG4 = "zavrete_dvere_vytah_ide_dole_obrazok4.png"

# Funkcia na zobrazenie hlášky agenta
def issuecoin_hlaska(kategoria, suma):
    hlasky = {
        "Potraviny": [
            "Pozor, minul si na potraviny viac ako 6500 Kč – to asi bude chladnička mlsať 😆",
            "Tento nákup vyzerá ako zásoba na celý mesiac! 🛒",
            "To bude plná chladnička, však? 😋",
            "Dúfam, že si nezabudol kúpiť aj zeleninu! 🥦"
        ],
        "Oblečenie": [
            "Nová móda? Alebo si len dopĺňaš šatník? 😄",
            "Fashion week u teba doma? 🧥👗",
            "Hlavne nech je to pohodlné a štýlové! 😎"
        ]
    }
    if kategoria in hlasky and suma > 6500:
        return random.choice(hlasky[kategoria])
    return ""

# 🛗 Obrazovka 1 – Výber dátumu
st.image(IMG1, use_column_width=True)
st.subheader("Vitaj vo výdavkovom výťahu 🛗")
datum = st.date_input("Vyber dátum svojho nákupu", datetime.today())

if datum:
    with st.spinner("Výťah sa otvára..."):
        time.sleep(2)
    st.image(IMG2, use_column_width=True)
    time.sleep(2)

    # 🧾 Obrazovka 3 – Výdavková aplikácia
    st.subheader("Zadaj svoje výdavky")

    krajina = st.selectbox("Vyber krajinu", ["Česká republika", "Slovensko", "Rakúsko"])
    kategoria = st.selectbox("Vyber kategóriu", ["Potraviny", "Oblečenie", "Bývanie", "Zábava", "Iné"])
    suma = st.number_input("Zadaj sumu výdavku", min_value=0)

    if st.button("Uložiť výdavok"):
        st.success(f"Výdavok {suma} Kč v kategórii {kategoria} bol uložený.")

        # 💬 AI agent hláška
        hlaska = issuecoin_hlaska(kategoria, suma)
        if hlaska:
            st.info(f"IssueCoin ti vraví: {hlaska}")

        # 📉 Môžeš sem doplniť aj ukladanie do CSV, grafy, atď.
        time.sleep(2)
        st.image(IMG4, use_column_width=True)
        st.write("Výťah ide späť na prízemie... 👋")

