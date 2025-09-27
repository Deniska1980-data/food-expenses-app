import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Výdavkový denník – CZK + CNB TXT feed", layout="wide")

# Inicializácia session state
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(
        columns=["Date", "Shop", "Country", "Currency", "Amount",
                 "Category", "Note", "Converted_CZK", "Rate_date", "Rate_value"]
    )

# Funkcia pre načítanie kurzov z TXT feedu ČNB
def get_cnb_rate(date_str, code):
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date_str}"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None, None

    lines = response.text.split("\n")
    if len(lines) < 2:
        return None, None, None

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

# Mapovanie krajín a mien
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

# Mapovanie kategórií na ikony a farby
category_icons = {
    "Potraviny 🛒": "#FFA500",
    "Drogérie 🧴": "#1f77b4",
    "Doprava 🚌": "#2ca02c",
    "Reštaurácie a bary 🍽️": "#9467bd",
    "Zábava 🎉": "#d62728",
    "Odevy 👕": "#8c564b",
    "Obuv 👟": "#e377c2",
    "Elektronika 💻": "#7f7f7f",
    "Domácnosť / nábytok 🛋️": "#bcbd22",
    "Šport a voľný čas 🏀": "#17becf",
    "Zdravie a lekáreň 💊": "#ff7f0e",
    "Cestovanie / dovolenka ✈️": "#1f77b4",
    "Vzdelávanie / kurzy 📚": "#2ca02c",
}

st.title("💰 Výdavkový denník – CZK + CNB TXT feed")
st.markdown("CZK = vždy 1:1. Ostatné meny podľa denného kurzového lístka ČNB. "
            "Ak nie je kurz dostupný, použije sa posledný známy.")

# Vstupy
date = st.date_input("📅 Dátum nákupu", datetime.today())
country = st.selectbox("🌍 Krajina + mena", list(countries.keys()))
amount = st.number_input("💵 Suma", min_value=0.0, step=1.0)
category = st.selectbox("📂 Kategória", list(category_icons.keys()))
shop = st.text_input("🏬 Obchod / miesto")
note = st.text_input("📝 Poznámka")

# Uloženie nákupu
if st.button("💾 Uložiť nákup"):
    currency_code = countries[country]
    converted = None
    rate_value = None
    rate_date = date.strftime("%Y-%m-%d")

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
        st.success(f"Nákup pridaný! Prepočet: {round(converted,2)} CZK (kurz {round(rate_value,4)} k {rate_date})")

        # 🔔 Jemné a hravé hlášky podľa kategórií
        df_check = pd.DataFrame(st.session_state["expenses"])
        cat_sum = df_check.groupby("Category")["Converted_CZK"].sum()

        if "Potraviny 🛒" in cat_sum and cat_sum["Potraviny 🛒"] > 6000:
            st.info("🍎 Nakúpené ako pre celú rodinu! Dobrú chuť a nech chladnička vydrží plná čo najdlhšie. 😋")

        if "Zábava 🎉" in cat_sum and cat_sum["Zábava 🎉"] > 2000:
            st.warning("🎉 Zábavy nikdy nie je dosť! Len pozor, aby ti ešte zostalo aj na chlebík. 😉")

        if "Drogérie 🧴" in cat_sum and cat_sum["Drogérie 🧴"] > 2000:
            st.info("🧴 To je ale voňavý košík! Prášky, plienky, šampóny… hlavne, že doma bude čisto a voňavo. 🌸")

        if "Elektronika 💻" in cat_sum and cat_sum["Elektronika 💻"] > 5000:
            st.info("💻 Nový kúsok do zbierky? Hlavne nech ti vydrží dlho a uľahčí deň. 🚀")

    else:
        st.error(f"❌ Kurz pre {currency_code} sa nepodarilo načítať.")

# -----------------------------
# Filter podľa mesiaca a roku
# -----------------------------
if not st.session_state["expenses"].empty:
    st.subheader("🔎 Filter výdavkov")
    months = sorted(set(pd.to_datetime(st.session_state["expenses"]["Date"]).dt.month))
    years = sorted(set(pd.to_datetime(st.session_state["expenses"]["Date"]).dt.year))

    sel_year = st.selectbox("Rok", years, index=len(years)-1)
    sel_month = st.selectbox("Mesiac", months, index=len(months)-1)

    df_filtered = st.session_state["expenses"][
        (pd.to_datetime(st.session_state["expenses"]["Date"]).dt.year == sel_year) &
        (pd.to_datetime(st.session_state["expenses"]["Date"]).dt.month == sel_month)
    ]
else:
    df_filtered = pd.DataFrame()

# -----------------------------
# Zobrazenie tabuľky
# -----------------------------
st.subheader("📋 Zoznam nákupov")
st.dataframe(df_filtered, use_container_width=True)

# -----------------------------
# Súhrn a graf
# -----------------------------
if not df_filtered.empty:
    total = df_filtered["Converted_CZK"].sum()
    st.subheader("📊 Súhrn mesačných výdavkov")
    st.metric("Celkové výdavky", f"{total:.2f} CZK")

    # Skupina podľa kategórií
    grouped = df_filtered.groupby("Category")["Converted_CZK"].sum().reset_index()

    chart = alt.Chart(grouped).mark_bar().encode(
        x=alt.X("Category", sort="-y", title="Kategória"),
        y=alt.Y("Converted_CZK", title="Výdavky CZK"),
        color=alt.Color("Category", scale=alt.Scale(domain=list(category_icons.keys()),
                                                   range=list(category_icons.values())),
                        legend=None),
        tooltip=["Category", "Converted_CZK"]
    ).properties(
        width=700,
        height=400,
        title=f"Graf výdavkov podľa kategórií – {sel_month}/{sel_year}"
    )

    text = chart.mark_text(
        align="center", baseline="bottom", dy=-5
    ).encode(text="Converted_CZK:Q")

    st.altair_chart(chart + text, use_container_width=True)
