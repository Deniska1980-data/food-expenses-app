import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta, datetime
import requests
from io import BytesIO

st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Mapovanie krajina -> mena podľa CNB ---
country_currency_map = {
    "Česko": "CZK",
    "Eurozóna / Slovensko": "EUR",
    "USA": "USD",
    "Veľká Británia": "GBP",
    "Švajčiarsko": "CHF",
    "Poľsko": "PLN",
    "Maďarsko": "HUF",
    "Švédsko": "SEK",
    "Nórsko": "NOK",
    "Dánsko": "DKK",
    "Japonsko": "JPY",
    "Austrália": "AUD",
    "Kanada": "CAD",
    "Čína": "CNY",
    "Hongkong": "HKD",
    "Kórea": "KRW",
    "Rusko": "RUB",
    "Turecko": "TRY",
    "Južná Afrika": "ZAR",
    "Bulharsko": "BGN",
    "Rumunsko": "RON",
    "Island": "ISK",
    "Mexiko": "MXN",
    "Izrael": "ILS",
    "Brazília": "BRL",
    "India": "INR",
    "Iné": None
}

# --- Funkcia na získanie kurzu z ČNB ---
def get_cnb_rate(currency: str, date_in: dt_date):
    """
    Vráti (rate, used_date) podľa ČNB.
    Ak je dnešný deň a ešte nie je 14:30 → použije včerajší kurz.
    """
    now = datetime.now()
    d = date_in

    # logika 14:30 pre dnešný dátum
    if d == dt_date.today():
        if now.hour < 14 or (now.hour == 14 and now.minute < 30):
            d = d - timedelta(days=1)

    while d >= dt_date(2024, 1, 1):
        url = f"https://api.cnb.cz/cnbapi/exrates/daily?date={d.isoformat()}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for rate in data["rates"]:
                    if rate["code"] == currency:
                        return float(rate["rate"]) / float(rate["amount"]), d
            d -= timedelta(days=1)
        except Exception:
            d -= timedelta(days=1)
    return 1.0, date_in  # fallback (CZK)

# --- Texty ---
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
    "categories": ["Potraviny", "Doprava", "Zábava", "Reštaurácie", "Iné"],
    "rate_notice": "ℹ️ Kurzy ČNB sa vyhlasujú každý pracovný deň o **14:30**. "
                   "Do tejto doby platí kurz z predchádzajúceho dňa.",
    "export_csv": "📥 Stiahnuť ako CSV",
    "export_xlsx": "📥 Stiahnuť ako Excel",
    "filter": "📅 Filtrovať podľa dátumu",
    "range": "Vlastný rozsah",
    "this_month": "Tento mesiac",
    "last_month": "Minulý mesiac",
    "this_year": "Tento rok"
}

texts_en = {
    "title": "💸 My Monthly Expense Diary",
    "intro": "Log your expenses and stay in control ☀️",
    "add": "➕ Add purchase",
    "date": "📅 Date",
    "shop": "🏪 Shop",
    "country": "🌍 Country",
    "currency": "💱 Currency",
    "amount": "💰 Amount",
    "category": "📂 Category",
    "note": "📝 Note",
    "save": "💾 Save purchase",
    "added": "✅ Purchase added!",
    "list": "📊 List of Purchases",
    "summary": "📈 Monthly Summary",
    "total": "💰 Total",
    "empty": "No purchases yet.",
    "categories": ["Food", "Transport", "Entertainment", "Restaurants", "Other"],
    "rate_notice": "ℹ️ CNB exchange rates are published every working day at **14:30**. "
                   "Until then, the previous day's rate is valid.",
    "export_csv": "📥 Download as CSV",
    "export_xlsx": "📥 Download as Excel",
    "filter": "📅 Filter by Date",
    "range": "Custom Range",
    "this_month": "This Month",
    "last_month": "Last Month",
    "this_year": "This Year"
}

# --- Výber jazyka ---
col1, col2 = st.columns([8, 2])
with col2:
    lang = st.radio("", ["🇸🇰 Slovensko/Česko", "🇬🇧 English"], index=0)

t = texts_sk if lang.startswith("🇸🇰") else texts_en

# --- Inicializácia dát ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount",
        "Category", "Note", "Rate", "Converted_CZK", "Rate_date"
    ])

# --- Nadpis ---
st.title(t["title"])
st.markdown(t["intro"])
st.info(t["rate_notice"])

# --- Formulár ---
st.subheader(t["add"])
with st.form("input_form"):
    date_in = st.date_input(t["date"], value=dt_date.today(), min_value=dt_date(2024, 1, 1))
    shop = st.text_input(t["shop"])
    
    country = st.selectbox(t["country"], list(country_currency_map.keys()))
    if country == "Iné":
        currency = st.selectbox(
            t["currency"],
            [c for c in country_currency_map.values() if c is not None]
        )
    else:
        currency = country_currency_map[country]
    
    amount = st.number_input(t["amount"], min_value=0.0, step=0.5)
    category = st.selectbox(t["category"], t["categories"])
    note = st.text_input(t["note"])
    
    submitted = st.form_submit_button(t["save"])

    if submitted:
        rate, rate_date = get_cnb_rate(currency, date_in)
        converted = amount * rate
        new_record = {
            "Date": date_in,
            "Shop": shop,
            "Country": country,
            "Currency": currency,
            "Amount": amount,
            "Category": category,
            "Note": note,
            "Rate": round(rate, 4),
            "Converted_CZK": round(converted, 2),
            "Rate_date": rate_date
        }
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([new_record])],
            ignore_index=True
        )
        st.success(t["added"])

# --- Výpis nákupov ---
st.subheader(t["list"])
st.dataframe(st.session_state.data, use_container_width=True)

# --- Súhrn + Export s filtrom ---
st.subheader(t["summary"])
if not st.session_state.data.empty:
    total_sum = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"### {t['total']}: {total_sum:.2f} CZK")

    # 🔹 Filter podľa dátumu + rýchle voľby
    st.subheader(t["filter"])
    option = st.radio("", [t["range"], t["this_month"], t["last_month"], t["this_year"]])

    today = dt_date.today()
    if option == t["this_month"]:
        start_date = today.replace(day=1)
        end_date = today
    elif option == t["last_month"]:
        first_day_this_month = today.replace(day=1)
        last_month_last_day = first_day_this_month - timedelta(days=1)
        start_date = last_month_last_day.replace(day=1)
        end_date = last_month_last_day
    elif option == t["this_year"]:
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            start_date = st.date_input("Od", value=st.session_state.data["Date"].min())
        with col_f2:
            end_date = st.date_input("Do", value=st.session_state.data["Date"].max())

    filtered_data = st.session_state.data[
        (st.session_state.data["Date"] >= pd.to_datetime(start_date)) &
        (st.session_state.data["Date"] <= pd.to_datetime(end_date))
    ]

    st.dataframe(filtered_data, use_container_width=True)

    # --- Export tlačidlá ---
    today_str = today.isoformat()
    csv = filtered_data.to_csv(index=False).encode("utf-8")
    st.download_button(t["export_csv"], csv, f"expenses_{today_str}.csv", "text/csv")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        filtered_data.to_excel(writer, index=False, sheet_name="Expenses")
    st.download_button(t["export_xlsx"], output.getvalue(),
                       f"expenses_{today_str}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.info(t["empty"])

# --- Info o kurze ---
if not st.session_state.data.empty:
    last_rate_date = st.session_state.data["Rate_date"].iloc[-1]
    st.caption(f"ℹ️ Kurz ČNB platný k dátumu: {last_rate_date}")

