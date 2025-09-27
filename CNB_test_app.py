import streamlit as st
import pandas as pd
import requests
from datetime import date as dt_date, timedelta

st.set_page_config(page_title="Výdavkový denník", layout="centered")

# --- CNB kurzy podľa dátumu ---
def get_cnb_rate(chosen_date, currency_code):
    """
    Získa kurz z CNB pre daný dátum a menu.
    Ak kurz nie je dostupný (víkend/sviatok), použije posledný dostupný od 1.1.2024 nižšie.
    Vracia (rate_per_1_unit_in_czk, used_date) alebo (None, None).
    """
    base_url = "https://api.cnb.cz/cnbapi/exrates/daily"
    d = chosen_date

    while d >= dt_date(2024, 1, 1):  # iba od 1.1.2024
        url = f"{base_url}?date={d.isoformat()}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # premena na kurz za 1 jednotku meny (CNB vracia rate pre 'amount' jednotiek)
                rates = {r["code"]: (float(r["rate"].replace(",", ".")) / r["amount"]) for r in data["rates"]}
                if currency_code in rates:
                    return rates[currency_code], d
        except Exception:
            pass
        d -= timedelta(days=1)

    return None, None


# --- Mapovanie kódov mien na krajiny/oblasti (iba meny dostupné v CNB) ---
cnb_countries = {
    "CZK": "Česko / Czechia",
    "EUR": "Eurozóna / Eurozone",
    "USD": "USA",
    "GBP": "Veľká Británia / United Kingdom",
    "CHF": "Švajčiarsko / Switzerland",
    "PLN": "Poľsko / Poland",
    "HUF": "Maďarsko / Hungary",
    "HRK": "Chorvátsko / Croatia",
    "SEK": "Švédsko / Sweden",
    "NOK": "Nórsko / Norway",
    "DKK": "Dánsko / Denmark",
    "AUD": "Austrália / Australia",
    "CAD": "Kanada / Canada",
    "JPY": "Japonsko / Japan",
    "CNY": "Čína / China"
}

# --- Texty ---
texts_sk = {
    "title": "💸 Môj mesačný výdavkový denník („Výdejový deník“)",
    "intro": "Zaznamenaj si svoje nákupy a výdavky – nech máš prehľad, aj keď si na dovolenke ☀️",
    "add": "➕ Pridať nákup / Přidat nákup",
    "date": "📅 Dátum nákupu / Datum nákupu",
    "shop": "🏪 Obchod / miesto (Obchod / místo)",
    "country": "🌍 Krajina / Mena",
    "amount": "💰 Suma / Suma",
    "category": "📂 Kategória / Kategorie",
    "note": "📝 Poznámka",
    "save": "💾 Uložiť nákup / Uložit nákup",
    "added": "✅ Nákup bol pridaný! / Nákup byl přidán!",
    "list": "📊 Zoznam nákupov / Seznam nákupů",
    "summary": "📈 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů",
    "total": "💰 Celkové výdavky / Celkové výdaje",
    "tip_high": "💡 Pozor! Na zábavu míňaš viac ako 30 %. Skús odložiť časť bokom 😉",
    "tip_info": "Najviac si minul(a) na _{cat}_ ({pct:.1f} %).",
    "empty": "Zatiaľ nemáš žiadne nákupy.",
    "categories": ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"],
    "caption": "ℹ️ Kurzy ČNB sa vyhlasujú každý pracovný deň o **14:30**. Ak pre zvolený dátum ešte nie sú k dispozícii (víkend/sviatok), použije sa **posledný dostupný kurz**."
}

texts_en = {
    "title": "💸 My Monthly Expense Diary",
    "intro": "Log your expenses – even while on holiday ☀️",
    "add": "➕ Add Purchase",
    "date": "📅 Date",
    "shop": "🏪 Shop",
    "country": "🌍 Country / Currency",
    "amount": "💰 Amount",
    "category": "📂 Category",
    "note": "📝 Note",
    "save": "💾 Save purchase",
    "added": "✅ Purchase added!",
    "list": "📊 Purchase List",
    "summary": "📈 Monthly Summary",
    "total": "💰 Total Expenses",
    "tip_high": "💡 Warning! More than 30% spent on fun. Try to save 😉",
    "tip_info": "Most spent on _{cat}_ ({pct:.1f} %).",
    "empty": "No purchases yet.",
    "categories": ["Food", "Drugstore", "Transport", "Restaurants & Bars", "Entertainment"],
    "caption": "ℹ️ CNB publishes FX rates on **business days at 14:30**. If no rate exists for the chosen date (weekend/holiday), the **last available rate** is used."
}

# --- Výber jazyka ---
col1, col2 = st.columns([8, 2])
with col2:
    lang = st.radio("", ["🇸🇰 Slovensko/Česko", "🇬🇧 English"], index=0)

t = texts_sk if lang.startswith("🇸🇰") else texts_en

# --- Init dataframe ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# --- Title ---
st.title(t["title"])
st.markdown(t["intro"])

# --- Formulár ---
st.subheader(t["add"])
with st.form("input_form"):
    date_in = st.date_input(t["date"], value=dt_date.today(), min_value=dt_date(2024, 1, 1))
    shop = st.text_input(t["shop"])
    country_currency = st.selectbox(t["country"], [f"{v} ({k})" for k, v in cnb_countries.items()])
    amount = st.number_input(t["amount"], min_value=0.0, step=0.5)
    category = st.selectbox(t["category"], t["categories"])
    note = st.text_input(t["note"])
    submitted = st.form_submit_button(t["save"])

# 🔎 malé upozornenie pod formulárom (caption)
st.caption(t["caption"])

# spracovanie po submit-e
if 'submitted' in locals() and submitted:
    code = country_currency.split("(")[-1].replace(")", "").strip()
    rate, rate_date = get_cnb_rate(date_in, code)
    if rate:
        converted = round(amount * rate, 2)
        new_row = {
            "Date": date_in,
            "Shop": shop,
            "Country": country_currency,
            "Currency": code,
            "Amount": amount,
            "Category": category,
            "Note": note,
            "Converted_CZK": converted,
            "Rate_date": rate_date
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success(t["added"])
    else:
        st.error("❌ Kurz pre túto menu a dátum nebol nájdený.")

# --- Zoznam nákupov ---
st.subheader(t["list"])
st.dataframe(st.session_state.data, use_container_width=True)

# --- Súhrn ---
st.subheader(t["summary"])
if not st.session_state.data.empty:
    total = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"### {t['total']}: {total:.2f} CZK")
    by_cat = st.session_state.data.groupby("Category")["Converted_CZK"].sum()
    for cat, val in by_cat.items():
        st.markdown(f"**{cat}:** {val:.2f} CZK")
    top_cat = by_cat.idxmax()
    pct = by_cat[top_cat] / total * 100
    if (lang.startswith("🇸🇰") and top_cat == "Zábava") or (lang.startswith("🇬🇧") and top_cat == "Entertainment"):
        if pct > 30:
            st.warning(t["tip_high"])
    else:
        st.info(t["tip_info"].format(cat=top_cat, pct=pct))
else:
    st.info(t["empty"])
