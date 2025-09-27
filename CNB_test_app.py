import streamlit as st
import pandas as pd
from datetime import date as dt_date

import requests
st.subheader("💱 Aktuálne kurzy ČNB")

# URL API ČNB – denné kurzy
url = "https://api.cnb.cz/cnbapi/exrates/daily"

try:
    response = requests.get(url)
    data = response.json()

    # prevedieme na DataFrame pre pekné zobrazenie
    rates = pd.DataFrame(data["rates"])
    st.dataframe(rates)

except Exception as e:
    st.error(f"Chyba pri načítaní kurzov: {e}")


st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Language Switch (top right with flags) ---
col1, col2 = st.columns([8, 2])
with col2:
    lang = st.radio(
        "",
        ["🇸🇰 Slovensko/Česko", "🇬🇧 English"],
        index=0,
        horizontal=False
    )

# --- Slovak & Czech texts ---
texts_sk = {
    "title": "💸 Môj mesačný výdavkový denník („Výdejový deník“)",
    "intro": "Zaznamenaj si svoje nákupy a výdavky – nech máš prehľad, aj keď si na dovolenke ☀️ / "
             "Zaznamenej si své nákupy a výdaje – ať máš přehled, i když jsi na dovolené ☀️",
    "add": "➕ Pridať nákup / Přidat nákup",
    "date": "📅 Dátum nákupu / Datum nákupu",
    "shop": "🏪 Obchod / miesto (Obchod / místo)",
    "country": "🌍 Krajina / Krajina",
    "currency": "💱 Mena / Měna",
    "amount": "💰 Suma / Suma",
    "category": "📂 Kategória / Kategorie",
    "note": "📝 Poznámka (napr. kúpený aj šampón, pivo v bare...) / "
            "Poznámka (např. koupený i šampon, pivo v baru...)",    
    "save": "💾 Uložiť nákup / Uložit nákup",
    "added": "✅ Nákup bol pridaný! / Nákup byl přidán!",
    "list": "📊 Zoznam nákupov / Seznam nákupů",
    "summary": "📈 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů",
    "total": "💰 Celkové výdavky / Celkové výdaje",
    "tip_high": "💡 Pozor! Na zábavu míňaš viac ako 30 %. "
                "Skús odložiť časť bokom na nečakané výdavky. 😉 / "
                "💡 Pozor! Na zábavu utrácíš více než 30 %. "
                "Zkus odložit část stranou na nečekané výdaje. 😉",
    "tip_info": "Najviac si minul(a) na _{cat}_ ({pct:.1f}% z celkových výdavkov).",
    "empty": "Zatiaľ nemáš žiadne nákupy. Pridaj aspoň jeden a uvidíš svoje dáta ✨ / "
             "Zatím nemáš žádné nákupy. Přidej alespoň jeden a uvidíš svá data ✨",
    "countries": ["Slovensko / Slovensko", "Česko / Česko", "Chorvátsko / Chorvatsko", "Iné / Jiné"],
    "currencies": ["CZK (Kč)", "EUR (€)", "USD ($)", "GBP (£)"],
    "categories": ["Potraviny / Potraviny", "Drogérie / Drogérie", "Doprava / Doprava", 
                   "Reštaurácie a bary / Restaurace a bary", "Zábava / Zábava"]
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
    "tip_high": "💡 Watch out! You’re spending more than 30% on entertainment. "
                "Try saving a portion for unexpected expenses. 😉",
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
st.subheader(t["summary"])

data = st.session_state.data

if not data.empty:
    total_sum = data["Converted_CZK"].sum()
    category_summary = data.groupby("Category")["Converted_CZK"].sum()

    for cat, amt in category_summary.items():
        st.markdown(f"**{cat}:** {amt:.2f} CZK")

    st.markdown(f"### {t['total']}: {total_sum:.2f} CZK")

    # --- Educational Tip ---
    top_category = category_summary.idxmax()
    percent = category_summary[top_category] / total_sum * 100
    if (top_category in ["Zábava / Zábava", "Entertainment"]) and percent > 30:
        st.warning(t["tip_high"])
    else:
        st.info(t["tip_info"].format(cat=top_category, pct=percent))
else:
    st.info(t["empty
