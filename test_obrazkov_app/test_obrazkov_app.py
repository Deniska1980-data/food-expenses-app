import streamlit as st
from datetime import date
from PIL import Image

# Nastavenie stránky
st.set_page_config(page_title="Výdavkový denník", layout="centered")

# Hlavička
st.markdown("## 🛗 Výdavkový denník / Výdajový deník")

# Načítanie obrázka výťahu (obrázok 1)
image_path = "images_vytah_appka/vytah_zavrete_dvere_obrazok1.png"
image = Image.open(image_path)

# Layout: Kalendár a jazykový prepínač zarovno s obrázkom
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.write("")  # prázdny riadok na vyrovnanie
with col2:
    # Funkčný výber dátumu
    selected_date = st.date_input("📅 Vyber dátum", date.today(), key="calendar_top")
    
    # Funkčný výber jazyka
    language = st.selectbox(
        "🌐 Zvoľ jazyk / Choose language",
        ["Slovensky / Česky", "English"],
        key="language_top"
    )
with col3:
    st.write("")

# Zobrazenie obrázka výťahu
st.image(image, use_column_width=True)

# Voliteľne: zobrazenie výberu jazyka a dátumu pod obrázkom
st.write(f"🔤 Jazyk: **{language}**")
st.write(f"📆 Dátum: **{selected_date.strftime('%Y-%m-%d')}**")
