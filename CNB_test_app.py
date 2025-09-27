import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta
import requests

# --- Nastavenie stránky ---
st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Funkcia na získanie kurzu z ČNB ---
def get_cnb_rate(code, chosen_date):
    """Načíta kurz z ČNB API pre daný dátum a menu.
       Ak kurz nie je dostupný, použije posledný dostupný deň pred týmto dátumom."""
    base_url = "https://api.cnb.cz/cnbapi/exrates/daily"
    check_date = chosen_date

    for _ in range(7):  # max. 7 dní späť
        url = f"{base_url}?date={check_date.isoformat()}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                rates = data.get("rates", [])
                if rates:
                    for r in rates:
                        if r["code"] == code:
                            rate = float(r["rate"].replace(",", "."))
                            amount = int(r["amount"])
                            return rate / amount, check_date
        except Exception:
            pass
        # ak nenájdeme, posunieme sa o deň späť
        check_date -= timedelta(days=1)

    return None, None

# --- Mapovanie krajín na meny ---
country_currency_map = {
    "Česko / Czechia": "CZK",
    "Nemecko / Germany": "EUR",
    "Francúzsko / France": "EUR",
    "Taliansko / Italy": "EUR",
    "Španielsko / Spain": "EUR",
    "Grécko / Greece": "EUR",
    "Slovensko / Slovakia": "EUR",
    "Chorvátsko / Croatia": "EUR",
    "Holandsko / Netherlands": "EUR",
    "Belgicko / Belgium": "EUR",
    "Fínsko / Finland": "EUR",
    "Írsko / Ireland": "EUR",
    "Portugalsko / Portugal": "EUR",
    "Luxembursko": "EUR",
    "Estónsko / Estonia": "EUR",
    "Lotyšsko / Latvia": "EUR",
    "Litva / Lithuania": "EUR",
    "Slovinsko / Slovenia": "EUR",
    "Cyprus": "EUR",
    "Malta": "EUR"
}

categories = ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"]

# --- Inicializácia dát ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount",
        "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# --- UI ---
st.title("💸 Môj mesačný výdavkový denník – test verzia CZK + EUR")
st.markdown("Zaznamenaj si nákupy v CZK alebo EUR – prepočítané podľa kurzov ČNB ☀️")

st.subheader("➕ Pridať nákup")

with st.form("input_form"):
    col1, col2 = st.columns(2)

    with col1:
        purchase_date = st.date_input("📅 Dátum nákupu", value=dt_date.today())
        shop = st.text_input("🏪 Obchod / miesto")
        country = st.selectbox("🌍 Krajina", list(country_currency_map.keys()))

    with col2:
        amount = st.number_input("💰 Suma", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Kategória", categories)

    note = st.text_input("📝 Poznámka")
    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        code = country_currency_map[country]

        # CZK = 1:1
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
            st.success(f"✅ Nákup pridaný! Prepočet: {converted} CZK (kurz z {rate_date})")
        else:
            st.error("❌ Kurz pre danú menu sa nepodarilo načítať.")

# --- Zobrazenie dát ---
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state.data, use_container_width=True)

# --- Súhrn ---
if not st.session_state.data.empty:
    st.subheader("📈 Súhrn výdavkov")
    total = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"💰 Celkové výdavky: **{total:.2f} CZK**")

# --- Info ---
st.caption("ℹ️ Kurzy ČNB sa vyhlasujú každý pracovný deň o 14:30. "
           "Ak pre zvolený dátum nie sú k dispozícii (víkend/sviatok), "
           "použije sa posledný dostupný kurz.")

