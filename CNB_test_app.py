import streamlit as st
import pandas as pd
import requests
import datetime
import altair as alt

# -------------------------------
# Funkcia pre CZK 1:1 a ostatné meny z CNB TXT feed
# -------------------------------
def get_cnb_rates(date: str):
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.text.split("\n")
        rates = {}
        for row in data[2:]:
            if row.strip():
                parts = row.split("|")
                if len(parts) == 5:
                    country, currency, amount, code, rate = parts
                    try:
                        rates[code] = float(rate.replace(",", ".")) / float(amount)
                    except:
                        continue
        return rates
    except Exception:
        return None

# -------------------------------
# Kategórie + prístupné farby
# -------------------------------
categories = {
    "Potraviny 🛒": "#FFA500",          # oranžová
    "Drogérie 🧴": "#1E90FF",          # modrá
    "Doprava 🚌": "#2E8B57",           # zelená
    "Reštaurácie a bary 🍽️": "#8A2BE2", # fialová
    "Zábava 🎉": "#DC143C",            # červená
    "Odevy 👕": "#20B2AA",             # tyrkysová
    "Obuv 👟": "#FFD700",              # žltá
    "Elektronika 💻": "#708090",       # sivá
    "Domácnosť / nábytok 🛋️": "#8B4513", # hnedá
    "Šport a voľný čas 🏀": "#32CD32", # svetlozelená
    "Zdravie a lekáreň 💊": "#FF69B4", # ružová
    "Cestovanie / dovolenka ✈️": "#00CED1", # tyrkysovo-modrá
    "Vzdelávanie / kurzy 📚": "#4169E1" # tmavomodrá
}

# -------------------------------
# Krajiny + meny
# -------------------------------
countries = {
    "Česko / Czechia – CZK Kč": "CZK",
    "Eurozóna – EUR €": "EUR",
    "USA – USD $": "USD",
    "Veľká Británia – GBP £": "GBP",
    "Švajčiarsko – CHF Fr": "CHF",
    "Poľsko – PLN zł": "PLN",
    "Maďarsko – HUF Ft": "HUF",
    "Dánsko – DKK kr": "DKK",
    "Japonsko – JPY ¥": "JPY",
    "Kanada – CAD $": "CAD",
    "Čína – CNY ¥": "CNY",
    "Brazília – BRL R$": "BRL",
    "Austrália – AUD $": "AUD",
    "Turecko – TRY ₺": "TRY",
    "Thajsko – THB ฿": "THB",
    "India – INR ₹": "INR",
    "Mexiko – MXN $": "MXN",
    "Izrael – ILS ₪": "ILS",
    "Nórsko – NOK kr": "NOK",
    "Švédsko – SEK kr": "SEK",
    "Južná Afrika – ZAR R": "ZAR"
}

# -------------------------------
# Inicializácia session state
# -------------------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(
        columns=["Date", "Shop", "Country", "Currency", "Amount",
                 "Category", "Note", "Converted_CZK", "Rate_date"]
    )

# -------------------------------
# Formulár na zadanie nákupu
# -------------------------------
st.subheader("➕ Pridať nákup")

with st.form("expense_form", clear_on_submit=True):
    date = st.date_input("📅 Dátum nákupu", datetime.date.today())
    shop = st.text_input("🏪 Obchod / miesto")
    country = st.selectbox("🌍 Krajina + mena", list(countries.keys()))
    amount = st.number_input("💰 Suma", min_value=0.0, step=1.0)
    category = st.selectbox("📂 Kategória", list(categories.keys()))
    note = st.text_input("📝 Poznámka")

    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        currency = countries[country]
        if currency == "CZK":
            rate = 1.0
            rate_date = date
        else:
            str_date = date.strftime("%d.%m.%Y")
            rates = get_cnb_rates(str_date)
            if not rates or currency not in rates:
                st.error(f"❌ Kurz pre {currency} sa nepodarilo načítať.")
                rate = None
                rate_date = None
            else:
                rate = rates[currency]
                rate_date = date

        if rate:
            converted = round(amount * rate, 2)
            new_row = pd.DataFrame(
                [[date, shop, country, currency, amount, category, note, converted, rate_date]],
                columns=st.session_state["expenses"].columns
            )
            st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_row], ignore_index=True)

            st.success(f"✅ Nákup pridaný! Prepočet: {converted} CZK (kurz z {rate_date})")

            # Humorné/poučné hlášky
            if category.startswith("Zábava") and converted > 2000:
                st.warning("🎉 To bola ale poriadna párty! Peňaženka sa ešte spamätáva. 😅")
            if category.startswith("Potraviny") and converted > 6000:
                st.warning("🛒 Plná špajza? Alebo si si kúpil(a) celý supermarket? 😆")
            if category.startswith("Elektronika") and converted > 10000:
                st.info("💻 Gratulujem! Ale skontroluj, či nepotrebuješ aj nový stôl na tú elektroniku. 😜")

# -------------------------------
# Zoznam nákupov
# -------------------------------
st.subheader("🧾 Zoznam nákupov")
st.dataframe(st.session_state["expenses"], use_container_width=True)

# -------------------------------
# Filter podľa mesiaca a roka
# -------------------------------
st.subheader("🗓️ Filter podľa mesiaca a roka")

if not st.session_state["expenses"].empty:
    st.session_state["expenses"]["Date"] = pd.to_datetime(st.session_state["expenses"]["Date"])

    years = sorted(st.session_state["expenses"]["Date"].dt.year.unique())
    selected_year = st.selectbox("Vyber rok", years, index=len(years)-1)

    months = {
        1: "Január", 2: "Február", 3: "Marec", 4: "Apríl",
        5: "Máj", 6: "Jún", 7: "Júl", 8: "August",
        9: "September", 10: "Október", 11: "November", 12: "December"
    }
    selected_month = st.selectbox("Vyber mesiac", list(months.keys()),
                                  format_func=lambda x: months[x],
                                  index=datetime.date.today().month-1)

    filtered = st.session_state["expenses"][
        (st.session_state["expenses"]["Date"].dt.year == selected_year) &
        (st.session_state["expenses"]["Date"].dt.month == selected_month)
    ]
else:
    filtered = pd.DataFrame()

# -------------------------------
# Súhrn mesačných výdavkov
# -------------------------------
st.subheader("📊 Súhrn mesačných výdavkov")

if filtered.empty:
    st.info("Žiadne výdavky za zvolené obdobie.")
else:
    total = filtered["Converted_CZK"].sum()
    st.metric("Celkové výdavky", f"{total:.2f} CZK")

    grouped = filtered.groupby("Category")["Converted_CZK"].sum().reset_index()

    # Altair graf s farbami podľa kategórie
    chart = alt.Chart(grouped).mark_bar().encode(
        x=alt.X("Category:N", title="Kategória"),
        y=alt.Y("Converted_CZK:Q", title="Výdavky v CZK"),
        color=alt.Color("Category:N",
                        scale=alt.Scale(domain=list(categories.keys()),
                                        range=list(categories.values())),
                        legend=alt.Legend(title="Kategórie")),
        tooltip=["Category", "Converted_CZK"]
    ).properties(width=700, height=450)

    st.altair_chart(chart, use_container_width=True)

