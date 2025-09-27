import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta
import requests

st.set_page_config(page_title="Výdavkový denník – CZK + CNB TXT feed", layout="centered")

# =====================================
# Pomocné funkcie
# =====================================
CNB_TXT = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"

def fmt_cz(d: dt_date) -> str:
    return d.strftime("%d.%m.%Y")

def fetch_cnb_rate(for_date: dt_date, code: str, max_back_days: int = 10):
    """Načíta kurz z CNB TXT feedu podľa kódu meny."""
    check_date = for_date
    for _ in range(max_back_days + 1):
        url = f"{CNB_TXT}?date={fmt_cz(check_date)}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and resp.text:
                lines = resp.text.strip().splitlines()
                if len(lines) >= 3:
                    header_date = lines[0].split(" ")[0]
                    for line in lines[2:]:
                        parts = line.split("|")
                        if len(parts) >= 5 and parts[3] == code:
                            amount = int(parts[2])
                            rate = float(parts[4].replace(",", "."))
                            per_one = rate / amount
                            dd, mm, yyyy = header_date.split(".")
                            valid_iso = f"{yyyy}-{mm}-{dd}"
                            return per_one, valid_iso
        except Exception:
            pass
        check_date -= timedelta(days=1)
    return None, None

# =====================================
# Krajiny a meny podľa CNB feedu (26.09.2025)
# =====================================
COUNTRY_OPTIONS = {
    "Česko / Czechia – CZK Kč": "CZK",   # manuálne 1:1
    "Austrália – AUD $": "AUD",
    "Brazília – BRL R$": "BRL",
    "Bulharsko – BGN лв": "BGN",
    "Čína – CNY ¥": "CNY",
    "Dánsko – DKK kr": "DKK",
    "Eurozóna – EUR €": "EUR",
    "Filipíny – PHP ₱": "PHP",
    "Hongkong – HKD $": "HKD",
    "India – INR ₹": "INR",
    "Indonézia – IDR Rp": "IDR",
    "Island – ISK kr": "ISK",
    "Izrael – ILS ₪": "ILS",
    "Japonsko – JPY ¥": "JPY",
    "Južná Afrika – ZAR R": "ZAR",
    "Kanada – CAD $": "CAD",
    "Kórea – KRW ₩": "KRW",
    "Maďarsko – HUF Ft": "HUF",
    "Malajzia – MYR RM": "MYR",
    "Mexiko – MXN $": "MXN",
    "MMF – XDR": "XDR",
    "Nórsko – NOK kr": "NOK",
    "Nový Zéland – NZD $": "NZD",
    "Poľsko – PLN zł": "PLN",
    "Rumunsko – RON lei": "RON",
    "Singapur – SGD $": "SGD",
    "Švédsko – SEK kr": "SEK",
    "Švajčiarsko – CHF Fr.": "CHF",
    "Thajsko – THB ฿": "THB",
    "Turecko – TRY ₺": "TRY",
    "USA – USD $": "USD",
    "Veľká Británia – GBP £": "GBP"
}

CATEGORIES = ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"]

# =====================================
# Session state
# =====================================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount",
        "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# =====================================
# UI
# =====================================
st.title("💸 Výdavkový denník – CZK + CNB TXT feed")
st.caption("CZK = 1:1. Ostatné meny podľa denného kurzového lístka ČNB. Ak nie je kurz dostupný, použije sa posledný známy.")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        purchase_date = st.date_input("📅 Dátum nákupu", value=dt_date.today())
        shop = st.text_input("🏪 Obchod / miesto")
        country_display = st.selectbox("🌍 Krajina + mena", list(COUNTRY_OPTIONS.keys()))
    with col2:
        amount = st.number_input("💰 Suma", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Kategória", CATEGORIES)

    note = st.text_input("📝 Poznámka")
    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        rate, rate_date = None, None
        currency_code = COUNTRY_OPTIONS[country_display]

        if currency_code == "CZK":
            rate, rate_date = 1.0, purchase_date.strftime("%Y-%m-%d")
        else:
            rate, rate_date = fetch_cnb_rate(purchase_date, currency_code)

        if rate:
            converted = round(amount * rate, 2)
            new_record = {
                "Date": purchase_date,
                "Shop": shop,
                "Country": country_display,
                "Currency": currency_code,
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
            st.success(f"✅ Nákup pridaný! Prepočet: {converted} CZK (kurz ČNB z {rate_date})")
        else:
            st.error(f"❌ Kurz pre {currency_code} sa nepodarilo načítať.")

# =====================================
# Výpis dát
# =====================================
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state.data, use_container_width=True)

if not st.session_state.data.empty:
    st.subheader("📈 Súhrn")
    total = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"💰 Celkové výdavky: **{total:.2f} CZK**")

st.caption("ℹ️ Kurzy ČNB sa vyhlasujú pracovné dni po 14:30. "
           "Ak pre zvolený dátum nie je kurz dostupný (víkend/sviatok), použije sa posledný dostupný kurz.")

