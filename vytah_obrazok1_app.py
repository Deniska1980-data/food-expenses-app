import streamlit as st
from PIL import Image
import datetime

# Nastavenie názvu stránky
st.set_page_config(page_title="Výdavkový denník – Výtahový mód", page_icon="🧾")

# Nadpis aplikácie
st.markdown("## 🧾 Výdavkový denník – Výtahový mód")

# Zobrazenie obrázku č. 1 – výťah so zatvorenými dverami
obrazok = Image.open("images_vytah_appka/vytah_zavrete_dvere_obrazok1.png")
st.image(obrazok, caption="Obrázok č. 1 – Začiatok cesty výťahom", use_column_width=True)

# Rozdelenie obrazovky na 2 stĺpce, aby boli kalendár a jazyk vedľa seba
col1, col2 = st.columns(2)

with col1:
    # Reálny kalendárik na výber dátumu
    datum = st.date_input("📅 Vyber dátum:", datetime.date.today())

with col2:
    # Reálny prepínač jazyka (s vlajkami v texte)
    jazyk = st.selectbox("🌐 Vyber jazyk:", ["🇸🇰 Slovenský", "🇨🇿 Český", "🇬🇧 Anglický"])

# Potvrdenie výberov pre používateľa (dá sa neskôr upraviť alebo skryť)
st.success(f"✅ Zvolený dátum: {datum}")
st.info(f"🌍 Zvolený jazyk: {jazyk}")
