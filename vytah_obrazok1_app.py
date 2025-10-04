import streamlit as st
import datetime

# Nastav stránku bez rozťahovania
st.set_page_config(layout="wide")

# CSS štýl pre pozíciu prepínačov NAD obrázok
st.markdown("""
    <style>
    .container {
        position: relative;
        width: 100%;
        max-width: 700px;
        margin: auto;
    }

    .background-img {
        width: 100%;
        display: block;
    }

    .date-box {
        position: absolute;
        top: 52%;    /* nastav podľa potreby */
        left: 32%;   /* nastav podľa potreby */
        transform: translate(-50%, -50%);
        z-index: 2;
    }

    .language-box {
        position: absolute;
        top: 52%;
        left: 70%;
        transform: translate(-50%, -50%);
        z-index: 2;
    }

    </style>
""", unsafe_allow_html=True)

# Vytvor kontajner s obrázkom a widgetmi
st.markdown('<div class="container">', unsafe_allow_html=True)

# Reálny výber dátumu
with st.container():
    st.markdown('<div class="date-box">', unsafe_allow_html=True)
    datum = st.date_input("", value=datetime.date.today(), key="datum_vytah")
    st.markdown('</div>', unsafe_allow_html=True)

# Reálny výber jazyka
with st.container():
    st.markdown('<div class="language-box">', unsafe_allow_html=True)
    jazyk = st.selectbox("", ["🇸🇰 Slovenčina", "🇨🇿 Čeština", "🌐 English"], key="jazyk_vytah")
    st.markdown('</div>', unsafe_allow_html=True)

# Pozadie – obrázok výťahu
st.markdown(f'<img class="background-img" src="https://raw.githubusercontent.com/TVOJE_UZIVATELSKE_MENO/Food-Expenses-App/main/images_vytah_appka/vytah_zatvorene_dvere.png" />', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Pokračovanie aplikácie až po výbere dátumu
if datum:
    st.success(f"Zvolený dátum: {datum}")
    st.info(f"Zvolený jazyk: {jazyk}")
    # Tu môžeš spustiť ďalší krok: otvorenie výťahu, obrázok č. 2

