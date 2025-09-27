import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta
import requests

st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Funkcia na získanie kurzu ČNB ---
def get_cnb_rate(currency_code, chosen_date):
    """Vracia kurz voči CZK pre danú menu a dátum, fallback na posledný dostupný deň."""
    if currency_code == "CZK":
        return 1.0, chosen_date  # CZK je vždy 1:1

    base_url = "https://api.cnb.cz/cnbapi/exrates/daily"
    check_date = chosen_date

    for _ in range(7):  # max. 7 dní späť
        url = f"{base_url}?date={check_date}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                for r in data.get("rates", []):
                    if r["currencyCode"] == currency_code:
                        rate = float(r["rate"])
                        amount = int(r["amount"])
                        return rate / amount, r["validFor"]
        except Exception:
            pass
        # ak nenájdeme, posunieme sa o deň späť
        prev_date = dt_date.fromisoformat(check_date) - timedelta(days=1)
        check_date = prev_date.strftime("%Y-%m-%d")

    return None, None

# --- Krajiny a meny (CZK + EUR) ---
countries = {
    "Česko / Czechia": "CZK",
    "Nemecko / Germany": "EUR",
    "Francúzsko / France": "EUR",
    "Slovensko / Slovakia": "EUR",
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
st.title("💸 Výdavkový denník – CZK + EUR test")
st.markdown("Česko = CZK, eurozóna = EUR (kurzy ČNB).")

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
        rate, rate_date = get_cnb_rate(code, purchase_date.strftime("%Y-%m-%d"))

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
            st.error("❌ Kurz sa nepodarilo načítať.")

# --- Výpis dát ---
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state.data, use_container_width=True)

if not st.session_state.data.empty:
    st.subheader("📈 Súhrn")
    total = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"💰 Celkové výdavky: **{total:.2f} CZK**")

st.caption("ℹ️ Kurzy ČNB sa vyhlasujú každý pracovný deň o 14:30. "
           "Ak pre dátum nie sú k dispozícii (víkend/sviatok), použije sa posledný dostupný kurz.")


