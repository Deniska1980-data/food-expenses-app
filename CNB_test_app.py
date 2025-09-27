import streamlit as st
import pandas as pd
import requests
import datetime
import altair as alt

# -------------------------------
# Funkcia pre CZK 1:1 a ostatné meny z CNB TXT feed
# -------------------------------
def get_cnb_rates(date: str):
    """
    Stiahne kurzy z CNB TXT feedu pre daný dátum.
    Ak nie je kurz dostupný (víkend/sviatok), použije posledný dostupný.
    """
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date}"
    response = requests.get(url)

    if response.status_code != 200:
        return None, None

    lines = response.text.splitlines()
    if len(lines) < 3:
        return None, None

    # Prvý riadok obsahuje dátum kurzu
    rate_date = lines[0].split()[0]
    rates = {}
    for line in lines[2:]:
        parts = line.split('|')
        if len(parts) == 5:
            country, currency_name, amount, code, rate = parts
            amount = float(amount.replace(',', '.'))
            rate = float(rate.replace(',', '.'))
            rates[code] = rate / amount

    return rates, rate_date

# -------------------------------
# Nastavenie aplikácie
# -------------------------------
st.set_page_config(page_title="Výdavkový denník – CZK + CNB TXT feed", page_icon="💰")

st.title("💰 Výdavkový denník – CZK + CNB TXT feed")
st.caption("CZK = 1:1. Ostatné meny podľa denného kurzového lístka ČNB. "
           "Ak nie je kurz dostupný, použije sa posledný známy.")

# -------------------------------
# Dáta pre krajiny a meny
# -------------------------------
countries = {
    "Česko / Czechia – CZK Kč": "CZK",
    "Eurozóna – EUR €": "EUR",
    "USA – USD $": "USD",
    "Veľká Británia – GBP £": "GBP",
    "Švajčiarsko – CHF ₣": "CHF",
    "Poľsko – PLN zł": "PLN",
    "Maďarsko – HUF Ft": "HUF",
    "Dánsko – DKK kr": "DKK",
    "Nórsko – NOK kr": "NOK",
    "Švédsko – SEK kr": "SEK",
    "Kanada – CAD $": "CAD",
    "Austrália – AUD $": "AUD",
    "Japonsko – JPY ¥": "JPY",
    "Čína – CNY ¥": "CNY",
    "Turecko – TRY ₺": "TRY",
    "Brazília – BRL R$": "BRL",
    "Mexiko – MXN $": "MXN",
    "Južná Afrika – ZAR R": "ZAR",
    "India – INR ₹": "INR",
    "Izrael – ILS ₪": "ILS",
    "Thajsko – THB ฿ (prepočet cez USD)": "USD",
    "Vietnam – VND ₫ (prepočet cez USD)": "USD",
    "Egypt – EGP £ (prepočet cez USD)": "USD",
    "Dubaj – AED (prepočet cez USD)": "USD",
    "Argentína – ARS (prepočet cez USD)": "USD",
    "Kuba – CUP (prepočet cez USD)": "USD"
}

# -------------------------------
# Rozšírené kategórie s piktogramami
# -------------------------------
categories = {
    "Potraviny 🥕": "orange",
    "Drogérie 🧴": "blue",
    "Doprava 🚌": "green",
    "Reštaurácie a bary 🍽️": "purple",
    "Zábava 🎉": "red",
    "Odevy 👕": "pink",
    "Obuv 👟": "brown",
    "Elektronika 💻": "gray",
    "Domácnosť / nábytok 🛋️": "olive",
    "Šport a voľný čas 🏀": "cyan",
    "Zdravie a lekáreň 💊": "teal",
    "Cestovanie / dovolenka ✈️": "gold",
    "Vzdelávanie / kurzy 📚": "violet"
}

# -------------------------------
# Session state pre dáta
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

with st.form("add_expense"):
    date = st.date_input("📅 Dátum nákupu", datetime.date.today())
    shop = st.text_input("🏬 Obchod / miesto")
    country = st.selectbox("🌍 Krajina + mena", list(countries.keys()))
    amount = st.number_input("💰 Suma", min_value=0.0, step=1.0)
    category = st.selectbox("📂 Kategória", list(categories.keys()))
    note = st.text_input("📝 Poznámka")

    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        code = countries[country]

        if code == "CZK":
            rate = 1.0
            rate_date = str(date)
        else:
            rates, rate_date = get_cnb_rates(date.strftime("%d.%m.%Y"))
            if rates and code in rates:
                rate = rates[code]
            else:
                st.error(f"❌ Kurz pre {country} sa nepodarilo načítať.")
                rate = None

        if rate:
            converted = amount * rate
            new_row = {
                "Date": str(date),
                "Shop": shop,
                "Country": country,
                "Currency": code,
                "Amount": amount,
                "Category": category,
                "Note": note,
                "Converted_CZK": converted,
                "Rate_date": rate_date
            }
            st.session_state["expenses"] = pd.concat(
                [st.session_state["expenses"], pd.DataFrame([new_row])],
                ignore_index=True
            )

            # ✅ Ľudské a poučné hlášky podľa kategórie a limitu
            if category.startswith("Zábava") and converted > 2000:
                st.warning("🎉 Uf, na zábavu si minul/a viac ako 2000 Kč! "
                           "Skús si odložiť niečo aj na horšie časy 😉")
            elif category.startswith("Potraviny") and converted > 6000:
                st.warning("🥕 Výdaje za potraviny prekročili 6000 Kč. "
                           "Možno je čas viac variť doma 🍳")
            else:
                st.success(f"✅ Nákup pridaný! Prepočet: {converted:.2f} CZK (kurz z {rate_date})")

# -------------------------------
# Zoznam nákupov
# -------------------------------
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state["expenses"])

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
st.subheader("🧾 Súhrn")

if filtered.empty:
    st.info("Žiadne výdavky za zvolené obdobie.")
else:
    total = filtered["Converted_CZK"].sum()
    st.write(f"💰 Celkové výdavky: **{total:.2f} CZK**")

    grouped = filtered.groupby("Category")["Converted_CZK"].sum().reset_index()
    grouped["Color"] = grouped["Category"].map(categories)

    # Tabuľka
    st.dataframe(grouped)

    # Stĺpcový graf
    st.subheader("📊 Graf výdavkov podľa kategórií")
    st.bar_chart(
        grouped.set_index("Category")["Converted_CZK"],
        color=grouped["Color"].tolist()
    )

    # Koláčový graf (Altair)
    st.subheader("🥧 Percentuálne podiely kategórií")
    pie_data = grouped.copy()
    pie_data["Percent"] = pie_data["Converted_CZK"] / pie_data["Converted_CZK"].sum()

    pie_chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta("Converted_CZK", stack=True),
        color=alt.Color("Category", legend=None),
        tooltip=["Category", "Converted_CZK", alt.Tooltip("Percent", format=".1%")]
    ).properties(width=400, height=400)

    st.altair_chart(pie_chart, use_container_width=True)

    # -------------------------------
    # Export dát (CSV a Excel)
    # -------------------------------
    st.subheader("📂 Export dát")

    # CSV export
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Stiahnuť ako CSV",
        data=csv,
        file_name=f"vydavky_{selected_year}_{selected_month}.csv",
        mime="text/csv"
    )

    # Excel export
    excel_file = pd.ExcelWriter("/tmp/export.xlsx", engine="xlsxwriter")
    filtered.to_excel(excel_file, index=False, sheet_name="Výdavky")
    excel_file.close()
    with open("/tmp/export.xlsx", "rb") as f:
        st.download_button(
            label="⬇️ Stiahnuť ako Excel",
            data=f,
            file_name=f"vydavky_{selected_year}_{selected_month}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

