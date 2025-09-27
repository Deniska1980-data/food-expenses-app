import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta
import requests

st.set_page_config(page_title="Výdavkový denník CZK + EUR", layout="centered")

# --- Funkcia pre CZK ---
def get_czk_rate(chosen_date):
    return 1.0, chosen_date  # vždy 1 CZK

# --- Funkcia pre EUR (TXT feed CNB) ---
def get_eur_rate(chosen_date):
    base_url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    check_date = chosen_date

    for _ in range(7):  # skúsime max 7 dní späť
        url = f"{base_url}?date={dt_date.fromisoformat(check_date).strftime('%d.%m.%Y')}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            lines = resp.text.split("\n")
            if len(lines) > 2:
                for line in lines[2:]:
                    parts = line.split("|")
                    if len(parts) >= 5 and parts[3] == "EUR":
                        amount = int(parts[2])
                        rate = float(parts[4].replace(",", "."))
                        return rate / amount, dt_date.fromisoformat(check_date).strftime("%Y-%m-%d")
        # fallback deň späť
        prev_date = dt_date.fromisoformat(check_date) - timedelta(days=1)
        check_date = prev_date.strftime("%Y-%m-%d")
    return None, None

# --- Definícia krajín ---
countries = {
    "Česko / Czechia – CZK Kč": "CZK",
    "Slovensko / Slovakia – EUR €": "EUR",
    "Nemecko / Germany – EUR €": "EUR",
    "Francúzsko / France – EUR €": "EUR",
    "Taliansko / Italy – EUR €": "EUR",
    "Španielsko / Spain – EUR €": "EUR",
    "Holandsko / Netherlands – EUR €": "EUR",
    "Belgicko / Belgium – EUR €": "EUR",
    "Fínsko / Finland – EUR €": "EUR",
    "Chorvátsko / Croatia – EUR €": "EUR"
}

categories = ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"]

# --- Session state ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount",
        "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# --- UI ---
st.title("💸 Výdavkový denník – CZK + EUR zvlášť kroky")

with st.form("input_form"):
    col1, col2 = st.columns(2)

    with col1:
        purchase_date = st.date_input("📅 Dátum nákupu", value=dt_date.today())
        shop = st.text_input("🏪 Obchod / miesto")
        country_display = st.selectbox("🌍 Krajina + mena", list(countries.keys()))

    with col2:
        amount = st.number_input("💰 Suma", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Kategória", categories)

    note = st.text_input("📝 Poznámka")
    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        code = countries[country_display]

        # --- CZK krok ---
        if code == "CZK":
            rate, rate_date = get_czk_rate(purchase_date.strftime("%Y-%m-%d"))

        # --- EUR krok ---
        elif code == "EUR":
            rate, rate_date = get_eur_rate(purchase_date.strftime("%Y-%m-%d"))

        else:
            rate, rate_date = None, None

        if rate:
            converted = round(amount * rate, 2)
            new_record = {
                "Date": purchase_date,
                "Shop": shop,
                "Country": country_display,
                "Currency": code,
                "Amount": amount,
                "Category": category,
                "Note": note,
                "Converted_CZK": converted,
                "Rate_date": rate_date
            }
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([new_record])],
                ignore_index=True
            )
            st.success(f"✅ Nákup pridaný! Prepočet: {converted} CZK (kurz z {rate_date})")
        else:
            st.error(f"❌ Kurz pre {code} sa nepodarilo načítať.")

# --- Výpis dát ---
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state.data, use_container_width=True)

if not st.session_state.data.empty:
    st.subheader("📈 Súhrn")
    total = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"💰 Celkové výdavky: **{total:.2f} CZK**")

st.caption("ℹ️ CZK = vždy 1 CZK. EUR = podľa ČNB (TXT feed). "
           "Kurzy sa vyhlasujú každý pracovný deň o 14:30. "
           "Ak pre dátum nie sú k dispozícii, použije sa posledný dostupný kurz.")

