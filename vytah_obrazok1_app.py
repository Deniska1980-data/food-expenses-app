import streamlit as st
from PIL import Image

# Nastavenie šírky stránky
st.set_page_config(layout="centered")

# Názov aplikácie
st.title("Výdavkový denník – Výťahový mód 🚪🛗")

# INFO: Načítanie obrázkov z priečinka images_vytah_appka
obrazok1 = Image.open("images_vytah_appka/vytah_zavrete_dvere_obrazok1.png")
obrazok2 = Image.open("images_vytah_appka/obrazok_vnutro_vytah_s_appko_obrazok2.JPG")
obrazok3 = Image.open("images_vytah_appka/zavrete_dvere_vytah_ide_dole_obrazok4.png")

# Zobrazenie jednotlivých obrázkov s komentármi
st.subheader("🎬 Začiatok cesty")
st.image(obrazok1, use_column_width=True, caption="Zatvorené dvere – prízemie (poschodie 0)")

st.subheader("🧮 Zadávanie výdavkov")
st.image(obrazok2, use_column_width=True, caption="Otvorený výťah s aplikáciou")

st.subheader("📉 Ukončenie nákupu")
st.image(obrazok3, use_column_width=True, caption="Zatvorené dvere – výťah ide dolu")

# Footer
st.markdown("---")
st.markdown("🧠 *Navrhnuté a vytvorené: Deniska1980-data*")
