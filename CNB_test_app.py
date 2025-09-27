import streamlit as st
import pandas as pd
from datetime import date as dt_date
import requests

st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Načítanie kurzov z ČNB API (len na pozadí) ---
def get_exchange_rates():
    url = "https://api.cnb.cz/cnbapi/exrates/daily"
    try:
        response = requests.get(url)
        data = response.json()
        # uložíme do slovníka: kód meny -> kurz
        rates = {item["code"]: float(item["rate"]) / float(item["amount"]) for item in data["rates"]}
        rates["CZK"] = 1.0  # česká koruna je základ
        return rates
    except Exception as e:
        st.error(f"Chyba pri načítaní kurzov ČNB: {e}")
        return {"CZK": 1.0, "EUR": 25.0, "USD": 23.0, "GBP": 29.0}  # záložné hodnoty

exchange_rates = get_exchange_rates()

# --- prepínač jazyka ---
col1, col2 = st.columns([8, 2])
with col2:
    lang = st.radio(
        "",
        ["🇸🇰 Slovensko/Česko", "🇬🇧 English"],
        index=0,
        horizontal=False
    )

# --- texty pre SK/EN ---
texts_sk = {
    "title": "💸 Môj mesačný výdavkový denník („Výdejový deník“)",
    "intro": "Zaznamenaj si svoje nákupy a výdavky – nech máš prehľad, aj keď si na dovolenke ☀️",
    "add": "➕ Pridať nákup / Přidat nákup",
    "date": "📅 Dátum nákupu / Datum nákupu",
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
    "tip_high": "💡 Pozor! Na zábavu míňaš viac ako 30 %. Skús odložiť časť bokom na nečakané výdavky. 😉",
    "tip_info": "Najviac si minul(a) na _{cat}_ ({pct:.1f}% z celkových výdavkov).",
    "empty": "Zatiaľ nemáš žiadne nákupy.",
    "countries": ["Slovensko", "Česko", "Chorvátsko", "Iné"],
    "currencies": ["CZK", "EUR", "USD", "GBP"],
    "categories": ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"]
}

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
    "tip_high": "💡 Watch out! You’re spending more than 30% on entertainment. 😉",
    "tip_info": "Most of your spending went to _{cat}_ ({pct:.1f}% of total expenses).",
    "empty": "No purchases yet.",
    "countries": ["Slovakia", "Czechia", "Croatia", "Other"],
    "currencies": ["CZK", "EUR", "USD", "GBP"],
    "categories": ["Food", "Drugstore", "Transport", "Restaurants & Bars", "Entertainment"]
}

t = texts_sk if lang.startswith("🇸🇰") else texts_en

# --- DataFrame init ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Converted_CZK"
    ])

# --- Title & Intro ---
st.title(t["title"])
st.markdown(t["intro"])

# --- Form ---
st.subheader(t["add"])
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input(t["date"], value=dt_date.today())
        shop = st.text_input(t["shop"])
        country = st.selectbox(t["country"], t["countries"])
    with col2:
        currency = st.selectbox(t["currency"], t["currencies"])
        amount = st.number_input(t["amount"], min_value=0.0, step=0.5)
        category = st.selectbox(t["category"], t["categories"])
    note = st.text_input(t["note"])
    submitted = st.form_submit_button(t["save"])

    if submitted:
        rate = exchange_rates.get(currency, 1.0)
        converted = amount * rate
        new_record = {
            "Date": date,
            "Shop": shop,
            "Country": country,
            "Currency": currency,
            "Amount": amount,
            "Category": category,
            "Note": note,
            "Converted_CZK": round(converted, 2)
        }
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([new_record])],
            ignore_index=True
        )
        st.success(t["added"])

# --- Table ---
st.subheader(t["list"])
st.dataframe(st.session_state.data, use_container_width=True)

# --- Summary ---
st.subheader(t["summary"])
data = st.session_state.data
if not data.empty:
    total_sum = data["Converted_CZK"].sum()
    category_summary = data.groupby("Category")["Converted_CZK"].sum()
    for cat, amt in category_summary.items():
        st.markdown(f"**{cat}:** {amt:.2f} CZK")
    st.markdown(f"### {t['total']}: {total_sum:.2f} CZK")
    top_category = category_summary.idxmax()
    percent = category_summary[top_category] / total_sum * 100
    if (top_category in ["Zábava", "Entertainment"]) and percent > 30:
        st.warning(t["tip_high"])
    else:
        st.info(t["tip_info"].format(cat=top_category, pct=percent))
else:
    st.info(t["empty"])

