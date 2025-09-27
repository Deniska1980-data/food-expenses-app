import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta, datetime
import requests

st.set_page_config(page_title="Výdavkový denník / Expense Diary", layout="centered")

# --- Language Switch ---
col1, col2 = st.columns([8, 2])
with col2:
    lang = st.radio("", ["🇸🇰 Slovensko/Česko", "🇬🇧 English"], index=0, horizontal=False)

# --- Slovak & Czech texts ---
texts_sk = {
    "title": "💸 Môj mesačný výdavkový denník („Výdejový deník“)",
    "intro": "Zaznamenaj si svoje nákupy a výdavky – nech máš prehľad, aj keď si na dovolenke ☀️",
    "add": "➕ Pridať nákup",
    "date": "📅 Dátum nákupu",
    "shop": "🏪 Obchod / miesto",
    "country": "🌍 Krajina",
    "currency": "💱 Mena",
    "amount": "💰 Suma",
    "category": "📂 Kategória",
    "note": "📝 Poznámka",
    "save": "💾 Uložiť nákup",
    "added": "✅ Nákup bol pridaný!",
    "list": "📊 Zoznam nákupov",
    "summary": "📈 Súhrn mesačných výdavkov",
    "total": "💰 Celkové výdavky",
    "empty": "Zatiaľ nemáš žiadne nákupy.",
    "cnb_info": "Použitý kurz ČNB z dátumu {date}",
    "cnb_notice": "ℹ️ Kurzy ČNB sa vyhlasujú každý pracovný deň o 14:30. "
                  "Do tejto doby platí kurz z predchádzajúceho dňa."
}

# --- English texts ---
texts_en = {
    "title": "💸 My Monthly Expense Diary",
    "intro": "Record your purchases and expenses – keep track, even on vacation ☀️",
    "add": "➕ Add Purchase",
    "date": "📅 Date",
    "shop": "🏪 Shop",
    "country": "🌍 Country",
    "currency": "💱 Currency",
    "amount": "💰 Amount",
    "category": "📂 Category",
    "note": "📝 Note",
    "save": "💾 Save purchase",
    "added": "✅ Purchase has been added!",
    "list": "📊 List of Purchases",
    "summary": "📈 Monthly Expense Summary",
    "total": "💰 Total Expenses",
    "empty": "No purchases yet.",
    "cnb_info": "Exchange rate from CNB dated {date}",
    "cnb_notice": "ℹ️ CNB exchange rates are updated every working day at 14:30. "
                  "Until then, the previous day's rate is applied."
}

# --- Language select ---
t = texts_sk if lang.startswith("🇸🇰") else texts_en

# --- Session state ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# --- Title ---
st.title(t["title"])
st.markdown(t["intro"])
st.info(t["cnb_notice"])  # info banner

# --- Function to get CNB exchange rate ---
def get_cnb_rate(currency: str, selected_date: dt_date):
    """Načíta kurz ČNB. Pred 14:30 berie kurz z predchádzajúceho dňa."""
    now = datetime.now()
    base_url = "https://api.cnb.cz/cnbapi/exrates/daily"

    # ak je dnes vybraný dátum a ešte nie je 14:30 -> posuň sa o deň späť
    if selected_date == dt_date.today() and now.hour < 14 or (now.hour == 14 and now.minute < 30):
        selected_date -= timedelta(days=1)

    # fallback do minulosti (napr. víkend/sviatok)
    d = selected_date
    while d >= dt_date(2024, 1, 1):
        try:
            resp = requests.get(f"{base_url}?date={d.isoformat()}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if currency == "CZK":
                    return 1.0, d
                for r in data["rates"]:
                    if r["code"] == currency:
                        return float(r["rate"]) / float(r["amount"]), d
        except Exception:
            pass
        d -= timedelta(days=1)
    return 1.0, selected_date

# --- Form ---
st.subheader(t["add"])
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input(t["date"], value=dt_date.today(), min_value=dt_date(2024, 1, 1))
        shop = st.text_input(t["shop"])
        country = st.text_input(t["country"])
    with col2:
        currency = st.selectbox(t["currency"], ["CZK", "EUR", "USD", "GBP"])
        amount = st.number_input(t["amount"], min_value=0.0, step=0.5)
        category = st.text_input(t["category"])
    note = st.text_input(t["note"])
    submitted = st.form_submit_button(t["save"])

    if submitted:
        rate, rate_date = get_cnb_rate(currency, date)
        converted = amount * rate
        new_record = {
            "Date": date,
            "Shop": shop,
            "Country": country,
            "Currency": currency,
            "Amount": amount,
            "Category": category,
            "Note": note,
            "Converted_CZK": round(converted, 2),
            "Rate_date": rate_date
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_record])], ignore_index=True)
        st.success(t["added"])

# --- Purchases list ---
st.subheader(t["list"])
st.dataframe(st.session_state.data, use_container_width=True)

# --- Summary ---
st.subheader(t["summary"])
data = st.session_state.data
if not data.empty:
    total_sum = data["Converted_CZK"].sum()
    st.markdown(f"### {t['total']}: {total_sum:.2f} CZK")

    # posledný použitý kurz
    last_rate_date = data["Rate_date"].max()
    st.caption(t["cnb_info"].format(date=last_rate_date))
else:
    st.info(t["empty"])
