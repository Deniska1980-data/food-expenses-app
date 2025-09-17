code = """
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Môj mesačný výdavkový denník", layout="centered")
st.title("💸 Môj mesačný výdavkový denník")

st.markdown("Zaznamenaj si svoje nákupy a výdavky – nech máš prehľad, aj keď si na dovolenke ☀️")

# --- Inicializácia dátového rámca ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Dátum", "Obchod", "Krajina", "Mena", "Suma", "Kategória", "Poznámka", "Prepočet_Kč"
    ])

# --- Formulár na zadávanie údajov ---
st.subheader("➕ Pridať nákup")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        datum = st.date_input("Dátum nákupu", value=date.today())
        obchod = st.text_input("Obchod / miesto")
        krajina = st.selectbox("Krajina", ["Česko", "Slovensko", "Chorvátsko", "Iné"])
    with col2:
        mena = st.selectbox("Mena", ["Kč", "€", "$", "£"])
        suma = st.number_input("Suma", min_value=0.0, format="%.2f")
        kategoria = st.selectbox("Kategória", ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"])

    poznamka = st.text_input("Poznámka (napr. kúpený aj šampón, pivo v bare...)")

    # 🔹 Zatiaľ fixné kurzy (neskôr CNB API)
    if mena == "€":
        kurz = 25.0
    elif mena == "$":
        kurz = 20.0
    elif mena == "£":
        kurz = 30.0
    else:
        kurz = 1.0

    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        prepocet = suma * kurz
        novy_zaznam = {
            "Dátum": datum,
            "Obchod": obchod,
            "Krajina": krajina,
            "Mena": mena,
            "Suma": suma,
            "Kategória": kategoria,
            "Poznámka": poznamka,
            "Prepočet_Kč": round(prepocet, 2)
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([novy_zaznam])], ignore_index=True)
        st.success("Nákup bol pridaný ✅")

# --- Zobrazenie tabuľky ---
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state.data, use_container_width=True)

# --- Výpočty ---
st.subheader("📈 Súhrn mesačných výdavkov")

data = st.session_state.data

if not data.empty:
    suma_celkovo = data["Prepočet_Kč"].sum()
    suhrn_kategorie = data.groupby("Kategória")["Prepočet_Kč"].sum()

    for kategoria, suma in suhrn_kategorie.items():
        st.markdown(f"**{kategoria}:** {suma:.2f} Kč")

    st.markdown(f"### 💰 Celkové výdavky: {suma_celkovo:.2f} Kč")

    # --- Edu tip ---
    top = suhrn_kategorie.idxmax()
    percento = suhrn_kategorie[top] / suma_celkovo * 100
    if top == "Zábava" and percento > 30:
        st.warning("💡 Pozor! Na zábavu míňaš viac ako 30 %. Skús odložiť časť bokom na nečakané výdavky. 😉")
    else:
        st.info(f"Najviac si minula na _{top}_ ({percento:.1f}% z celkových výdavkov).")
else:
    st.info("Zatiaľ nemáš žiadne nákupy. Pridaj aspoň jeden a uvidíš svoje dáta ✨")
"""

with open("app.py", "w") as f:
    f.write(code)


