import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Expense Diary", layout="wide")

# ---------------------------
# Prepínač jazyka hore vpravo (viditeľný selectbox)
# ---------------------------
col1, col2 = st.columns([8, 2])
with col2:
    language = st.selectbox(
        "🌐 Language / Jazyk",
        ["Slovensky / Česky", "English"],
        index=0
    )
lang = "cs" if language == "Slovensky / Česky" else "en"

# ---------------------------
# Texty podľa jazykov
# ---------------------------
TEXTS = {
    "cs": {
        "app_title": "💰 Výdavkový denník (Výdejový deník)",
        "purchase_date": "📅 Dátum nákupu / Datum nákupu",
        "country": "🌍 Krajina + mena / Krajina měna",
        "amount": "💵 Suma",
        "category": "📂 Kategória / Kategorie"
        "shop": "🏬 Obchod miesto / Obchod místo"
        "note": "📝 Poznámka",
        "save": "💾 Uložiť nákup / Uložit nákup",
        "list": "🧾 Zoznam nákupov / Seznam nákupů",
        "summary": "📊 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů",
        "total": "Celkové výdavky / Celkové výdaje",
        "filter": "🔎 Filter výdavkov / Filtr výdejů"
        "error_rate": "❌ Kurz sa nepodarilo načítať.",
    },
    "en": {
        "app_title": "💰 Expense Diary",
        "purchase_date": "📅 Purchase date",
        "country": "🌍 Country + currency",
        "amount": "💵 Amount",
        "category": "📂 Category",
        "shop": "🏬 Shop / place",
        "note": "📝 Note",
        "save": "💾 Save purchase",
        "list": "🧾 Purchase list",
        "summary": "📊 Monthly expenses summary",
        "total": "Total expenses",
        "filter": "🔎 Expense filter",
        "error_rate": "❌ Could not fetch exchange rate.",
    }
}

# ---------------------------
# Kategórie
# ---------------------------
CATEGORIES = {
    "cz": [
        "Potraviny 🛒", "Drogérie 🧴", "Doprava 🚌", "Reštaurácie a bary 🍽️",
        "Zábava 🎉", "Odevy 👕", "Obuv 👟", "Elektronika 💻",
        "Domácnosť / nábytok 🛋️", "Šport a voľný čas 🏀",
        "Zdravie a lekáreň 💊", "Cestovanie / dovolenka ✈️", "Vzdelávanie / kurzy 📚"
    ],
    "en": [
        "Groceries 🛒", "Drugstore 🧴", "Transport 🚌", "Restaurants & bars 🍽️",
        "Entertainment 🎉", "Clothing 👕", "Shoes 👟", "Electronics 💻",
        "Household / Furniture 🛋️", "Sports & Leisure 🏀",
        "Health & Pharmacy 💊", "Travel / Holiday ✈️", "Education / Courses 📚"
    ]
}

# ---------------------------
# Hlášky
# ---------------------------
MESSAGES = {
    "cz": {
        "food": "🍎 Nakúpené ako pre celú rodinu! Dobrú chuť a nech chladnička vydrží plná čo najdlhšie. 😋",
        "fun": "🎉 Zábavy nikdy nie je dosť! Len pozor, aby ti ešte zostalo aj na chlebík 😉",
        "drug": "🧴 To je ale voňavý košík! Prášky, plienky, šampóny… hlavne, že doma bude čisto a voňavo. 🌸",
        "elec": "💻 Nový kúsok do zbierky? Hlavne nech ti vydrží dlho a uľahčí deň. 🚀",
    },
    "en": {
        "food": "🍎 Groceries for the whole family! Enjoy your meals and may your fridge stay full. 😋",
        "fun": "🎉 There’s never enough fun! Just make sure you’ve still got some left for bread 😉",
        "drug": "🧴 That’s a fragrant basket! Detergents, diapers, shampoos… your home will be clean and fresh. 🌸",
        "elec": "💻 A new gadget? Hopefully it lasts long and makes life easier. 🚀",
    }
}

# ---------------------------
# Inicializácia session state
# ---------------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(
        columns=["Date", "Shop", "Country", "Currency", "Amount",
                 "Category", "Note", "Converted_CZK", "Rate_date", "Rate_value"]
    )

# ---------------------------
# Funkcia pre načítanie kurzov ČNB (TXT feed)
# ---------------------------
def get_cnb_rate(date_str, code):
    """
    TXT feed formát:
    země|měna|množství|kód|kurz
    Oddelovač: |
    Desatinný znak: , (nahrádza sa bodkou)
    """
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date_str}"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, None
    lines = response.text.split("\n")
    for line in lines[2:]:
        parts = line.strip().split("|")
        if len(parts) == 5:
            _, _, amount, c_code, rate = parts
            if c_code == code:
                try:
                    amount = float(amount.replace(",", "."))
                    rate = float(rate.replace(",", "."))
                    return rate, amount, date_str
                except ValueError:
                    return None, None, None
    return None, None, None

# ---------------------------
# Mapovanie krajín a mien
# ---------------------------
countries = {
    "Česko / Czechia – CZK Kč": "CZK",
    "Eurozóna – EUR €": "EUR",
    "USA – USD $": "USD",
    "Veľká Británia – GBP £": "GBP",
    "Poľsko – PLN zł": "PLN",
    "Maďarsko – HUF Ft": "HUF",
    "Švajčiarsko – CHF ₣": "CHF",
    "Dánsko – DKK kr": "DKK",
    "Kanada – CAD $": "CAD",
    "Japonsko – JPY ¥": "JPY",
}

# ---------------------------
# UI
# ---------------------------
st.title(TEXTS[lang]["app_title"])

date = st.date_input(TEXTS[lang]["purchase_date"], datetime.today())
country = st.selectbox(TEXTS[lang]["country"], list(countries.keys()))
amount = st.number_input(TEXTS[lang]["amount"], min_value=0.0, step=1.0)
category = st.selectbox(TEXTS[lang]["category"], CATEGORIES[lang])
shop = st.text_input(TEXTS[lang]["shop"])
note = st.text_input(TEXTS[lang]["note"])

# ---------------------------
# Uloženie nákupu
# ---------------------------
if st.button(TEXTS[lang]["save"]):
    currency_code = countries[country]
    converted, rate_value, rate_date = None, None, date.strftime("%Y-%m-%d")

    if currency_code == "CZK":
        converted = amount
        rate_value = 1.0
    else:
        d_str = date.strftime("%d.%m.%Y")
        rate, qty, rate_date = get_cnb_rate(d_str, currency_code)

        # fallback na posledný dostupný kurz
        if rate is None:
            url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.text.split("\n")
                for line in lines[2:]:
                    parts = line.strip().split("|")
                    if len(parts) == 5:
                        _, _, amount_txt, code_txt, rate_txt = parts
                        if code_txt == currency_code:
                            try:
                                qty = float(amount_txt.replace(",", "."))
                                rate = float(rate_txt.replace(",", "."))
                                rate_date = datetime.today().strftime("%Y-%m-%d")
                            except:
                                pass
                            break

        if rate:
            converted = amount * (rate / qty)
            rate_value = rate / qty

    if converted is not None:
        new_entry = pd.DataFrame([{
            "Date": date.strftime("%Y-%m-%d"),
            "Shop": shop,
            "Country": country,
            "Currency": currency_code,
            "Amount": amount,
            "Category": category,
            "Note": note,
            "Converted_CZK": round(converted, 2),
            "Rate_date": rate_date,
            "Rate_value": round(rate_value, 4) if rate_value else None
        }])
        st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_entry], ignore_index=True)
        st.success(f"{TEXTS[lang]['save']} OK: {round(converted,2)} CZK (kurz {round(rate_value,4)})")

        # Hlášky podľa kategórií
        df_check = pd.DataFrame(st.session_state["expenses"])
        cat_sum = df_check.groupby("Category")["Converted_CZK"].sum()

        if (("Potraviny 🛒" in cat_sum and cat_sum["Potraviny 🛒"] > 6000) or
            ("Groceries 🛒" in cat_sum and cat_sum["Groceries 🛒"] > 6000)):
            st.info(MESSAGES[lang]["food"])

        if (("Zábava 🎉" in cat_sum and cat_sum["Zábava 🎉"] > 2000) or
            ("Entertainment 🎉" in cat_sum and cat_sum["Entertainment 🎉"] > 2000)):
            st.warning(MESSAGES[lang]["fun"])

        if (("Drogérie 🧴" in cat_sum and cat_sum["Drogérie 🧴"] > 2000) or
            ("Drugstore 🧴" in cat_sum and cat_sum["Drugstore 🧴"] > 2000)):
            st.info(MESSAGES[lang]["drug"])

        if (("Elektronika 💻" in cat_sum and cat_sum["Elektronika 💻"] > 5000) or
            ("Electronics 💻" in cat_sum and cat_sum["Electronics 💻"] > 5000)):
            st.info(MESSAGES[lang]["elec"])
    else:
        st.error(TEXTS[lang]["error_rate"])

# ---------------------------
# Filter podľa mesiaca a roku
# ---------------------------
if not st.session_state["expenses"].empty:
    st.subheader(TEXTS[lang]["filter"])
    months = sorted(set(pd.to_datetime(st.session_state["expenses"]["Date"]).dt.month))
    years = sorted(set(pd.to_datetime(st.session_state["expenses"]["Date"]).dt.year))

    sel_year = st.selectbox("Rok / Year", years, index=len(years)-1)
    sel_month = st.selectbox("Mesiac / Month", months, index=len(months)-1)

    df_filtered = st.session_state["expenses"][
        (pd.to_datetime(st.session_state["expenses"]["Date"]).dt.year == sel_year) &
        (pd.to_datetime(st.session_state["expenses"]["Date"]).dt.month == sel_month)
    ]
else:
    df_filtered = pd.DataFrame()

# ---------------------------
# Tabuľka a graf
# ---------------------------
st.subheader(TEXTS[lang]["list"])
st.dataframe(df_filtered, use_container_width=True)

if not df_filtered.empty:
    total = df_filtered["Converted_CZK"].sum()
    st.subheader(TEXTS[lang]["summary"])
    st.metric(TEXTS[lang]["total"], f"{total:.2f} CZK")

    grouped = df_filtered.groupby("Category")["Converted_CZK"].sum().reset_index()
    chart = alt.Chart(grouped).mark_bar().encode(
        x=alt.X("Category", sort="-y", title=TEXTS[lang]["category"]),
        y=alt.Y("Converted_CZK", title="CZK"),
        tooltip=["Category", "Converted_CZK"]
    ).properties(width=700, height=400)
    st.altair_chart(chart, use_container_width=True)
