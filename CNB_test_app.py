import streamlit as st
import pandas as pd
import requests
import datetime
import altair as alt

# -----------------------
# Pomocné funkcie
# -----------------------

def get_czk_rate(date):
    """CZK = vždy 1:1"""
    return 1.0, date.strftime("%Y-%m-%d")

def get_currency_rate(date, currency_code):
    """Načíta kurz z denného TXT feedu ČNB pre danú menu"""
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/denni_kurz.txt?date={date.strftime('%d.%m.%Y')}"
    try:
        r = requests.get(url)
        r.encoding = "utf-8"
        lines = r.text.split("\n")
        for line in lines[2:]:
            parts = line.split("|")
            if len(parts) >= 5:
                kod = parts[3].strip()
                kurz = parts[4].replace(",", ".").strip()
                mnozstvi = parts[2].strip()
                if kod == currency_code:
                    rate = float(kurz) / float(mnozstvi)
                    return rate, date.strftime("%Y-%m-%d")
    except Exception as e:
        st.error(f"Chyba pri načítaní kurzu: {e}")
    return None, None

# -----------------------
# Konfigurácia kategórií a farieb
# -----------------------

categories = {
    "Potraviny 🛒": "orange",
    "Drogérie 🧴": "blue",
    "Doprava 🚗": "green",
    "Reštaurácie a bary 🍽️": "purple",
    "Zábava 🎉": "red",
    "Odevy 👕": "teal",
    "Obuv 👟": "brown",
    "Elektronika 💻": "gray",
    "Domácnosť / nábytok 🛋️": "pink",
    "Šport a voľný čas 🏀": "olive",
    "Zdravie a lekáreň 💊": "cyan",
    "Cestovanie / dovolenka ✈️": "magenta",
    "Vzdelávanie / kurzy 📚": "yellow",
}

# -----------------------
# Streamlit app
# -----------------------

st.set_page_config(page_title="Výdavkový denník – CZK + CNB TXT feed", layout="centered")

st.title("💰 Výdavkový denník – CZK + CNB TXT feed")
st.caption("CZK = 1:1. Ostatné meny podľa denného kurzového lístka ČNB.")

# Inicializácia session_state
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(
        columns=["Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Converted_CZK", "Rate_date"]
    )

# -----------------------
# Formulár na pridanie nákupu
# -----------------------

with st.form("add_expense"):
    date = st.date_input("📅 Dátum nákupu", datetime.date.today())
    country_currency = st.selectbox("🌍 Krajina + mena", [
        "Česko / Czechia – CZK Kč",
        "Eurozóna – EUR €",
        "USA – USD $",
        "Veľká Británia – GBP £",
        "Švajčiarsko – CHF ₣",
        "Poľsko – PLN zł",
        "Maďarsko – HUF Ft",
        "Dánsko – DKK kr",
        "Nórsko – NOK kr",
        "Švédsko – SEK kr",
        "Japonsko – JPY ¥",
        "Čína – CNY 元",
        "Kanada – CAD $",
        "Austrália – AUD $",
        "Brazília – BRL R$",
        "Turecko – TRY ₺",
        "India – INR ₹",
        "Izrael – ILS ₪",
        "Mexiko – MXN $",
        "Južná Afrika – ZAR R",
        "Thajsko – THB ฿"
    ])
    amount = st.number_input("💰 Suma", min_value=0.0, format="%.2f")
    category = st.selectbox("📂 Kategória", list(categories.keys()))
    shop = st.text_input("🏪 Obchod / miesto")
    note = st.text_input("📝 Poznámka")
    submit = st.form_submit_button("💾 Uložiť nákup")

if submit:
    # Určenie meny
    if "CZK" in country_currency:
        currency = "CZK"
        rate, rate_date = get_czk_rate(date)
    else:
        currency = country_currency.split("–")[-1].strip().split(" ")[0]
        rate, rate_date = get_currency_rate(date, currency)

    if rate:
        converted = float(amount) * rate
        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Shop": shop,
            "Country": country_currency,
            "Currency": currency,
            "Amount": float(amount),
            "Category": category,
            "Note": note,
            "Converted_CZK": float(converted),
            "Rate_date": rate_date,
        }
        st.session_state["expenses"] = pd.concat([st.session_state["expenses"], pd.DataFrame([new_row])], ignore_index=True)

        # Kontrolné hlášky
        if category == "Zábava 🎉" and converted > 2000:
            st.warning("🎭 Pozor! Za zábavu si minul/a viac ako 2000 Kč. Skús si odložiť niečo bokom 😉")
        if category == "Potraviny 🛒" and converted > 6000:
            st.warning("🛒 Uff! Viac ako 6000 Kč za potraviny tento mesiac. Nekŕmiš náhodou celú dedinu? 😆")

        st.success(f"✅ Nákup pridaný! Prepočet: {converted:.2f} CZK (kurz z {rate_date})")
    else:
        st.error(f"❌ Kurz pre {currency} sa nepodarilo načítať.")

# -----------------------
# Zobrazenie dát
# -----------------------

df = st.session_state["expenses"].copy()
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df["Converted_CZK"] = pd.to_numeric(df["Converted_CZK"], errors="coerce")

st.subheader("📜 Zoznam nákupov")
st.dataframe(df, use_container_width=True)

# -----------------------
# Súhrn
# -----------------------

total = df["Converted_CZK"].sum()
st.subheader("📊 Súhrn")
st.metric("Celkové výdavky", f"{total:,.2f} CZK")

# -----------------------
# Graf podľa kategórií
# -----------------------

if not df.empty:
    grouped = df.groupby("Category")["Converted_CZK"].sum().reset_index()
    grouped["Color"] = grouped["Category"].map(categories)

    chart = (
        alt.Chart(grouped)
        .mark_bar()
        .encode(
            x=alt.X("Category:N", sort="-y", title="Kategória"),
            y=alt.Y("Converted_CZK:Q", title="Výdavky v CZK"),
            color=alt.Color("Category:N", scale=alt.Scale(domain=list(categories.keys()), range=list(categories.values()))),
            tooltip=["Category", "Converted_CZK"]
        )
    )
    st.subheader("📈 Graf výdavkov podľa kategórií")
    st.altair_chart(chart, use_container_width=True)
