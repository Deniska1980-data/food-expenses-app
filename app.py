import streamlit as st
import pandas as pd
from datetime import date as dt_date

st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Language Switch (top right) ---
col1, col2 = st.columns([8,1])
with col2:
    lang = st.selectbox("Language", ["🇸🇰 SK (CZK)", "🇬🇧 ENG"], label_visibility="collapsed")

# --- Slovak texts ---
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
    "note": "📝 Poznámka (napr. kúpený aj šampón, pivo v bare...)",    
    "save": "💾 Uložiť nákup",
    "added": "✅ Nákup bol pridaný!",
    "list": "📊 Zoznam nákupov",
    "summary": "📈 Súhrn mesačných výdavkov",
    "total": "💰 Celkové výdavky",
    "tip_high": "💡 Pozor! Na zábavu míňaš viac ako 30 %. Skús odložiť časť bokom na nečakané výdavky. 😉",
    "tip_info": "Najviac si minul(a) na _{cat}_ ({pct:.1f}% z celkových výdavkov).",
    "empty": "Zatiaľ nemáš žiadne nákupy. Pridaj aspoň jeden a uvidíš svoje dáta ✨",
    "countries": ["Slovensko", "Česko", "Chorvátsko", "Iné"],
    "currencies": ["CZK", "EUR", "USD", "GBP"],
    "categories": ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"]
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
    "note": "📝 Note (e.g. shampoo, beer in bar...)",    
    "save": "💾 Save purchase",
    "added": "✅ Purchase has been added!",
    "list": "📊 List of Purchases",
    "summary": "📈 Monthly Expense Summary",
    "total": "💰 Total Expenses",
    "tip_high": "💡 Watch out! You’re spending more than 30% on entertainment. Try saving a portion for unexpected expenses. 😉",
    "tip_info": "Most of your spending went to _{cat}_ ({pct:.1f}% of total expenses).",
    "empty": "No purchases yet. Add at least one to see your data ✨",
    "countries": ["Slovakia", "Czechia", "Croatia", "Other"],
    "currencies": ["CZK (Czech koruna)", "EUR (Euro)", "USD (US Dollar)", "GBP (British Pound)"],
    "categories": ["Food", "Drugstore", "Transport", "Restaurants & Bars", "Entertainment"]
}

# --- Choose language ---
t = texts_sk if lang.startswith("🇸🇰") else texts_en

# --- Initialize DataFrame ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Converted_CZK"
    ])

# --- Title and Intro ---
st.title(t["title"])
st.markdown(t["intro"])

# --- Input Form ---
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

    # 🔹 Temporary fixed exchange rates (later: CNB API)
    if currency.startswith("EUR") or currency == "€":
        rate = 25.0
    elif currency.startswith("USD") or currency == "$":
        rate = 20.0
    elif currency.startswith("GBP") or currency == "£":
        rate = 30.0
    else:
        rate = 1.0

    if submitted:
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

# --- Display Table ---
st.subheader(t["list"])
st.dataframe(st.session_state.data, use_container_width=True)

# --- Calculations ---
st.subheader
