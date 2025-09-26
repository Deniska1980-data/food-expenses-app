import streamlit as st
import pandas as pd
from datetime import date as dt_date

st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- Slovak + Czech texts ---
texts = {
    "title": "💸 Môj mesačný výdavkový denník („Výdejový deník“)",
    "intro": "Zaznamenaj si svoje nákupy a výdavky – nech máš prehľad, aj keď si na dovolenke ☀️ "
             "/ Zaznamenej si své nákupy a výdaje – ať máš přehled, i když jsi na dovolené ☀️",
    "add": "➕ Pridať nákup / Přidat nákup",
    "date": "📅 Dátum nákupu / Datum nákupu",
    "shop": "🏪 Obchod / miesto (Obchod / místo)",
    "country": "🌍 Krajina / Krajina",
    "currency": "💱 Mena / Měna",
    "amount": "💰 Suma / Suma",
    "category": "📂 Kategória / Kategorie",
    "note": "📝 Poznámka / Poznámka (napr. kúpený aj šampón / koupený i šampón, pivo v bare...)",    
    "save": "💾 Uložiť nákup / Uložit nákup",
    "added": "✅ Nákup bol pridaný!",
    "list": "📊 Zoznam nákupov / Seznam nákupů",
    "summary": "📈 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů",
    "total": "💰 Celkové výdavky / Celkové výdaje",
    "tip_high": "💡 Pozor! Na zábavu míňaš viac ako 30 %. Skús odložiť časť bokom na nečakané výdavky. 😉 "
                "/ 💡 Pozor! Na zábavu utrácíš více než 30 %. Zkus odložit část stranou na nečekané výdaje. 😉",
    "tip_info": "Najviac si minul(a) na _{cat}_ ({pct:.1f}% z celkových výdavkov).",
    "empty": "Zatiaľ nemáš žiadne nákupy. Pridaj aspoň jeden a uvidíš svoje dáta ✨",
    "countries": ["Slovensko / Slovensko", "Česko / Česko", "Chorvátsko / Chorvatsko", "Iné / Jiné"],
    "currencies": ["CZK (Kč)", "EUR (€)", "USD ($)", "GBP (£)"],
    "categories": ["Potraviny / Potraviny", "Drogérie / Drogérie", "Doprava / Doprava",
                   "Reštaurácie a bary / Restaurace a bary", "Zábava / Zábava"]
}

# --- Initialize DataFrame ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Converted_CZK"
    ])

# --- Title and Intro ---
st.title(texts["title"])
st.markdown(texts["intro"])

# --- Input Form ---
st.subheader(texts["add"])

with st.form("input_form"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input(texts["date"], value=dt_date.today())
        shop = st.text_input(texts["shop"])
        country = st.selectbox(texts["country"], texts["countries"])

    with col2:
        currency = st.selectbox(texts["currency"], texts["currencies"])
        amount = st.number_input(texts["amount"], min_value=0.0, step=0.5)
        category = st.selectbox(texts["category"], texts["categories"])

    note = st.text_input(texts["note"])
    submitted = st.form_submit_button(texts["save"])

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
        st.success(texts["added"])

# --- Display Table ---
st.subheader(texts["list"])
st.dataframe(st.session_state.data, use_container_width=True)

# --- Calculations ---
st.subheader(texts["summary"])

data = st.session_state.data

if not data.empty:
    total_sum = data["Converted_CZK"].sum()
    category_summary = data.groupby("Category")["Converted_CZK"].sum()

    for cat, amt in category_summary.items():
        st.markdown(f"**{cat}:** {amt:.2f} CZK")

    st.markdown(f"### {texts['total']}: {total_sum:.2f} CZK")

    # --- Educational Tip ---
    top_category = category_summary.idxmax()
    percent = category_summary[top_category] / total_sum * 100
    if "Zábava" in top_category:
        if percent > 30:
            st.warning(texts["tip_high"])
        else:
            st.info(texts["tip_info"].format(cat=top_category, pct=percent))
    else:
        st.info(texts["tip_info"].format(cat=top_category, pct=percent))
else:
    st.info(texts["empty"])


