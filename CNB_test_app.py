import streamlit as st
import pandas as pd
import requests
from datetime import date as dt_date, timedelta

# --- Nastavenie aplikácie ---
st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Funkcia na získanie kurzu z ČNB ---
def get_cnb_rate(currency_code: str, purchase_date: dt_date):
    """Vracia kurz pre danú menu a dátum, alebo posledný dostupný kurz pred týmto dátumom."""
    check_date = purchase_date
    for _ in range(7):  # max. 7 dní späť
        url = f"https://api.cnb.cz/cnbapi/exrates/daily?date={check_date}"
        try:
            response = requests.get(url)
            data = response.json()
            rates = data.get("rates", [])
            if rates:
                for r in rates:
                    if r["code"] == currency_code:
                        # kurz sa počíta: kurz / množství
                        rate = float(r["rate"].replace(",", ".")) / int(r["amount"])
                        return rate, check_date
        except Exception as e:
            st.error(f"Chyba pri načítaní kurzov: {e}")
            return None, None
        # ak nenájdené → posuň deň späť
        check_date -= timedelta(days=1)
    return None, None

# --- Preddefinované meny a krajiny ---
currencies = {
    "CZK (Česká koruna)": "CZK",
    "EUR (Euro)": "EUR",
    "USD (US Dollar)": "USD",
    "GBP (British Pound)": "GBP",
    "CHF (Swiss Franc)": "CHF",
    "PLN (Polish Zloty)": "PLN",
    "HUF (Hungarian Forint)": "HUF"
}
countries = [
    "Česko / Czechia", "Slovensko / Slovakia", "Nemecko / Germany",
    "Rakúsko / Austria", "Poľsko / Poland", "Maďarsko / Hungary",
    "Veľká Británia / United Kingdom", "Švajčiarsko / Switzerland",
    "Iné / Other"
]
categories = ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"]

# --- Inicializácia session_state ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount",
        "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# --- UI ---
st.title("💸 Môj mesačný výdavkový denník („Výdejový deník“)")
st.markdown("Zaznamenaj si svoje nákupy a výdavky – vždy s aktuálnym kurzom ČNB ☀️")

st.subheader("➕ Pridať nákup / Přidat nákup")

with st.form("input_form"):
    col1, col2 = st.columns(2)

    with col1:
        purchase_date = st.date_input("📅 Dátum nákupu / Datum nákupu", value=dt_date.today(),
                                      min_value=dt_date(2024, 1, 1))
        shop = st.text_input("🏪 Obchod / miesto")
        country = st.selectbox("🌍 Krajina / Krajina", countries)

    with col2:
        currency_name = st.selectbox("💱 Mena / Měna", list(currencies.keys()))
        amount = st.number_input("💰 Suma / Suma", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Kategória / Kategorie", categories)

    note = st.text_input("📝 Poznámka")
    submitted = st.form_submit_button("💾 Uložiť nákup / Uložit nákup")

    if submitted:
        code = currencies[currency_name]
        if code == "CZK":
            rate, rate_date = 1.0, purchase_date
        else:
            rate, rate_date = get_cnb_rate(code, purchase_date)

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
            st.success("✅ Nákup bol pridaný! / Nákup byl přidán!")
        else:
            st.error("❌ Kurz pre danú menu sa nepodarilo načítať.")

# --- Info o kurzoch ---
st.caption("ℹ️ Kurzy ČNB sa vyhlasujú každý pracovný deň o 14:30. "
           "Ak pre zvolený dátum ešte nie sú k dispozícii (víkend/sviatok), použije sa posledný dostupný kurz.")

# --- Zoznam nákupov ---
st.subheader("📊 Zoznam nákupov / Seznam nákupů")
st.dataframe(st.session_state.data, use_container_width=True)

# --- Súhrn ---
if not st.session_state.data.empty:
    st.subheader("📈 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů")
    total = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"💰 Celkové výdavky: **{total:.2f} CZK**")


