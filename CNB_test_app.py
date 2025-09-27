import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Výdavkový denník – CNB feed", layout="centered")

# =====================================
# Pomocné funkcie – CNB TXT feed
# =====================================
CNB_TXT = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"

def fmt_cz(d: dt_date) -> str:
    return d.strftime("%d.%m.%Y")

def fetch_cnb_rate(for_date: dt_date, code: str, max_back_days: int = 10):
    """Načíta kurz z CNB TXT feedu podľa kódu meny s fallbackom."""
    check_date = for_date
    for _ in range(max_back_days + 1):
        url = f"{CNB_TXT}?date={fmt_cz(check_date)}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200 and resp.text:
                lines = resp.text.strip().splitlines()
                if len(lines) >= 3:
                    header_date = lines[0].split(" ")[0]
                    for line in lines[2:]:
                        parts = line.split("|")
                        if len(parts) >= 5 and parts[3] == code:
                            amount = int(parts[2])
                            rate = float(parts[4].replace(",", "."))
                            per_one = rate / amount
                            dd, mm, yyyy = header_date.split(".")
                            valid_iso = f"{yyyy}-{mm}-{dd}"
                            return per_one, valid_iso
        except Exception:
            pass
        check_date -= timedelta(days=1)
    return None, None

# =====================================
# Krajiny a meny (CZK = 1:1, ostatné podľa CNB feedu)
# =====================================
COUNTRY_OPTIONS = {
    "Česko / Czechia – CZK Kč": "CZK",
    "Eurozóna – EUR €": "EUR",
    "USA – USD $": "USD",
    "Veľká Británia – GBP £": "GBP",
    "Švajčiarsko – CHF Fr.": "CHF",
    "Poľsko – PLN zł": "PLN",
    "Maďarsko – HUF Ft": "HUF",
    "Nórsko – NOK kr": "NOK",
    "Dánsko – DKK kr": "DKK",
    "Švédsko – SEK kr": "SEK",
    "Kanada – CAD $": "CAD",
    "Austrália – AUD $": "AUD",
    "Nový Zéland – NZD $": "NZD",
    "Japonsko – JPY ¥": "JPY",
    "Čína – CNY ¥": "CNY",
    "India – INR ₹": "INR",
    "Brazília – BRL R$": "BRL",
    "Mexiko – MXN $": "MXN",
    "Južná Afrika – ZAR R": "ZAR",
    "Čile – CLP $": "CLP",
    "Turecko – TRY ₺": "TRY",
    "Izrael – ILS ₪": "ILS",
    "Maroko – MAD د.م.": "MAD",
    "Keňa – KES Sh": "KES",
    "Gruzínsko – GEL ₾": "GEL",
    "Arménsko – AMD ֏": "AMD",
    "Filipíny – PHP ₱": "PHP",
    "Hongkong – HKD $": "HKD",
    "Singapur – SGD $": "SGD",
    "Kórea – KRW ₩": "KRW",
    "Island – ISK kr": "ISK",
    "Rumunsko – RON lei": "RON",
    "Indonézia – IDR Rp": "IDR"
}

# =====================================
# Kategórie s piktogramami + limity
# =====================================
CATEGORIES = [
    "Potraviny 🛒",
    "Drogérie 🧴",
    "Doprava 🚌",
    "Reštaurácie a bary 🍽️",
    "Zábava 🎉",
    "Odevy 👕",
    "Obuv 👟",
    "Elektronika 💻",
    "Domácnosť / nábytok 🛋️",
    "Šport a voľný čas 🏀",
    "Zdravie a lekáreň 💊",
    "Cestovanie / dovolenka ✈️",
    "Vzdelávanie / kurzy 📚"
]

LIMITS = {
    "Potraviny 🛒": 6000,
    "Zábava 🎉": 2000,
    "Elektronika 💻": 10000,
    "Cestovanie / dovolenka ✈️": 30000
}

MESSAGES = {
    "Potraviny 🛒": "Pozor! Zdá sa, že doma zakladáš menší supermarket 🛒. Už si minul viac než 6000 Kč na potraviny!",
    "Zábava 🎉": "💡 Poučná rada: zábava je fajn, ale mysli aj na úspory. Na zábavu si už minul viac než 2000 Kč.",
    "Elektronika 💻": "Ups... 💻 To už je skoro nový notebook! Elektronika ťa vyšla cez 10 000 Kč.",
    "Cestovanie / dovolenka ✈️": "✈️ Haló cestovateľ! Vyzerá to, že už máš zakúpenú letenku na Mars – výdavky na cestovanie prekročili 30 000 Kč."
}

CATEGORY_COLORS = {
    "Potraviny 🛒": "orange",
    "Drogérie 🧴": "blue",
    "Doprava 🚌": "green",
    "Reštaurácie a bary 🍽️": "purple",
    "Zábava 🎉": "red",
    "Odevy 👕": "saddlebrown",
    "Obuv 👟": "navy",
    "Elektronika 💻": "gray",
    "Domácnosť / nábytok 🛋️": "tan",
    "Šport a voľný čas 🏀": "turquoise",
    "Zdravie a lekáreň 💊": "pink",
    "Cestovanie / dovolenka ✈️": "gold",
    "Vzdelávanie / kurzy 📚": "darkgreen"
}

# =====================================
# Session state
# =====================================
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount",
        "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# =====================================
# UI
# =====================================
st.title("💸 Výdavkový denník – CNB TXT feed")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        purchase_date = st.date_input("📅 Dátum nákupu", value=dt_date.today())
        shop = st.text_input("🏪 Obchod / miesto")
        country_display = st.selectbox("🌍 Krajina + mena", list(COUNTRY_OPTIONS.keys()))
    with col2:
        amount = st.number_input("💰 Suma", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Kategória", CATEGORIES)

    note = st.text_input("📝 Poznámka")
    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        rate, rate_date = None, None
        currency_code = COUNTRY_OPTIONS[country_display]

        if currency_code == "CZK":
            rate, rate_date = 1.0, purchase_date.strftime("%Y-%m-%d")
        else:
            rate, rate_date = fetch_cnb_rate(purchase_date, currency_code)

        if rate:
            converted = round(amount * rate, 2)
            new_record = {
                "Date": purchase_date,
                "Shop": shop,
                "Country": country_display,
                "Currency": currency_code,
                "Amount": amount,
                "Category": category,
                "Note": note,
                "Converted_CZK": converted,
                "Rate_date": rate_date
            }
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([new_record])],
                ignore_index=True
            )
            st.success(f"✅ Nákup pridaný! Prepočet: {converted} CZK (kurz ČNB z {rate_date})")
        else:
            st.error(f"❌ Kurz pre {currency_code} sa nepodarilo načítať.")

# =====================================
# Výpis dát + súhrn
# =====================================
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state.data, use_container_width=True)

if not st.session_state.data.empty:
    st.subheader("📈 Súhrn mesačných výdavkov")
    monthly_summary = st.session_state.data.groupby("Category")["Converted_CZK"].sum()

    for cat, total in monthly_summary.items():
        st.markdown(f"**{cat}:** {total:.2f} CZK")
        if cat in LIMITS and total > LIMITS[cat]:
            st.error(MESSAGES[cat])

    grand_total = monthly_summary.sum()
    st.markdown(f"💰 Celkové výdavky: **{grand_total:.2f} CZK**")

    # =====================================
    # Vizualizácia – stĺpcový graf
    # =====================================
    st.subheader("📊 Vizualizácia výdavkov podľa kategórií")

    colors = [CATEGORY_COLORS.get(cat, "lightgray") for cat in monthly_summary.index]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(monthly_summary.index, monthly_summary.values, color=colors)

    ax.set_ylabel("Výdavky (CZK)")
    ax.set_title("Výdavky podľa kategórií")
    plt.xticks(rotation=45, ha="right")

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.0f} Kč',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center", va="bottom")

    st.pyplot(fig)

st.caption("ℹ️ CZK = 1:1, ostatné meny podľa denného kurzového lístka ČNB. "
           "Kurzy sa vyhlasujú každý pracovný deň po 14:30. "
           "Ak pre zvolený dátum nie je kurz dostupný (víkend/sviatok), použije sa posledný dostupný kurz.")
