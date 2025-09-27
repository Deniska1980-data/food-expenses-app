import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta
import requests

st.set_page_config(page_title="Výdavkový denník – CZK + EUR", layout="centered")

# --- Funkcia: CZK je vždy 1 ---
def get_czk_rate(chosen_date):
    """CZK sa vždy rovná 1 CZK."""
    return 1.0, chosen_date

# --- Funkcia: EUR z ČNB API ---
def get_eur_rate(chosen_date):
    """Získa kurz EUR/CZK z ČNB podľa dátumu (fallback na posledný pracovný deň)."""
    base_url = "https://api.cnb.cz/cnbapi/exrates/daily"
    check_date = chosen_date

    for _ in range(7):  # fallback max 7 dní
        url = f"{base_url}?date={check_date}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                rates = data.get("rates", [])
                for r in rates:
                    if r.get("currencyCode") == "EUR":
                        rate = r["rate"]
                        if isinstance(rate, str):
                            rate = float(rate.replace(",", "."))
                        else:
                            rate = float(rate)
                        amount = int(r["amount"])
                        return rate / amount, data["validFor"]
        except Exception as e:
            print("Chyba EUR:", e)

        # ak kurz neexistuje → posunieme sa deň späť
        prev_date = dt_date.fromisoformat(check_date) - timedelta(days=1)
        check_date = prev_date.strftime("%Y-%m-%d")

    return None, None

# --- Zoznam krajín ---
countries = {
    "Česko / Czechia": "CZK",
    "Slovensko / Slovakia": "EUR",
    "Nemecko / Germany": "EUR",
    "Francúzsko / France": "EUR",
    "Taliansko / Italy": "EUR",
    "Španielsko / Spain": "EUR",
    "Holandsko / Netherlands": "EUR",
    "Belgicko / Belgium": "EUR",
    "Fínsko / Finland": "EUR",
    "Chorvátsko / Croatia": "EUR",
    "Grécko / Greece": "EUR",
    "Portugalsko / Portugal": "EUR",
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
        country = st.selectbox("🌍 Krajina", list(countries.keys()))

    with col2:
        amount = st.number_input("💰 Suma", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Kategória", categories)

    note = st.text_input("📝 Poznámka")
    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        code = countries[country]

        # 🔹 Krok 1: CZK
        if code == "CZK":
            rate, rate_date = get_czk_rate(purchase_date.strftime("%Y-%m-%d"))

        # 🔹 Krok 2: EUR
        elif code == "EUR":
            rate, rate_date = get_eur_rate(purchase_date.strftime("%Y-%m-%d"))

        else:
            rate, rate_date = None, None

        if rate:
            converted = round(amount * rate, 2)
            new_record = {
                "Date": purchase_date,
                "Shop": shop,
                "Country": country,
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

st.caption("ℹ️ CZK = vždy 1 CZK. EUR = podľa ČNB API. "
           "Kurzy sa vyhlasujú každý pracovný deň o 14:30. "
           "Ak pre dátum nie sú k dispozícii, použije sa posledný dostupný kurz.")


