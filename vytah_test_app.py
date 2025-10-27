import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, date as dt_date
from random import choice

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="💰 Výdavkový denník", layout="wide")

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
    html, body, [class*="css"] { font-size: 16px; line-height: 1.6; }
    h1 { font-size: 28px !important; }
    h2 { font-size: 24px !important; }
    h3 { font-size: 20px !important; }
    .stButton>button { font-size: 18px; padding: 10px 20px; }
    .stSelectbox>div>div { font-size: 16px; }
    .lang-select { position: absolute; top: 20px; right: 30px; z-index: 999; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR – Calendarific API key
# ---------------------------
with st.sidebar:
    st.subheader("⚙️ Nastavenia / Settings")
    CALENDARIFIC_API = st.text_input("🔑 Calendarific API key (optional)", type="password")

# ---------------------------
# LANGUAGE SELECTOR (top-right corner)
# ---------------------------
lang_placeholder = st.empty()
with lang_placeholder.container():
    col_lang = st.columns([8, 2])[1]
    with col_lang:
        lang_choice = st.selectbox("🌐 Jazyk / Language", ["Slovensky / Česky", "English"], index=0)
LANG = "sk" if "Slovensky" in lang_choice else "en"

# ---------------------------
# TEXTS
# ---------------------------
TEXTS = {
    "sk": {
        "app_title": "💰 Výdavkový denník / Výdajový deník",
        "subtitle": "CZK = vždy 1:1. Ostatné meny podľa denného kurzu ČNB. "
                    "Ak pre vybraný deň nie je kurz, použije sa posledný dostupný kurz.",
        "date": "📅 Dátum nákupu / Datum nákupu",
        "country": "🌍 Krajina + mena / Měna",
        "amount": "💵 Suma / Částka",
        "category": "📂 Kategória / Kategorie",
        "shop": "🏬 Obchod / miesto",
        "note": "📝 Poznámka",
        "save": "💾 Uložiť nákup / Uložit nákup",
        "list": "🧾 Zoznam nákupov / Seznam nákupů",
        "summary": "📊 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů",
        "total": "Celkové výdavky / Celkové výdaje",
        "rate_err": "❌ Kurz sa nepodarilo načítať.",
        "saved_ok": "Záznam uložený!",
        "rate_info": "Použitý kurz",
        "rate_from": "k",
        "holiday": "🎉 Štátny sviatok / svátek:",
        "export": "💾 Exportovať do CSV"
    },
    "en": {
        "app_title": "💰 Expense Diary",
        "subtitle": "CZK = always 1:1. Other currencies follow CNB daily rates. "
                    "If no rate is available for the selected date, the last available rate is used.",
        "date": "📅 Purchase date",
        "country": "🌍 Country + currency",
        "amount": "💵 Amount",
        "category": "📂 Category",
        "shop": "🏬 Shop / place",
        "note": "📝 Note",
        "save": "💾 Save purchase",
        "list": "🧾 Purchase list",
        "summary": "📊 Monthly expenses summary",
        "total": "Total expenses",
        "rate_err": "❌ Could not fetch exchange rate.",
        "saved_ok": "Saved!",
        "rate_info": "Applied rate",
        "rate_from": "as of",
        "holiday": "🎉 Public holiday:",
        "export": "💾 Export CSV"
    }
}

# ---------------------------
# CATEGORIES
# ---------------------------
CATEGORIES = {
    "sk": ["Potraviny 🛒", "Zábava 🎉", "Drogérie 🧴", "Elektronika 💻"],
    "en": ["Groceries 🛒", "Entertainment 🎉", "Drugstore 🧴", "Electronics 💻"]
}

# ---------------------------
# ISSUECOIN SEASON LOGIC 🌸☀️🍂❄️
# ---------------------------
def get_season_avatar():
    month = datetime.now().month

    if month in [12, 1, 2]:
        return (
            "❄️ IssueCoin má šál, rukavice a hrnček kakaa ☕ – "
            "vonku sneží, blížia sa Vianoce 🎄 a Silvester 🎆!"
        )
    elif month in [3, 4, 5]:
        return (
            "🌷 IssueCoin sadí kvety 🌼, zbiera vajíčka 🥚 a usmieva sa – "
            "jar je tu! Cvičí, behá a má plno energie! 💪🌸"
        )
    elif month in [6, 7, 8]:
        return (
            "☀️ IssueCoin má okuliare 😎, je pri mori 🌊 a dáva si zmrzlinu 🍦 – "
            "leto, dovolenka a prázdniny sú v plnom prúde! 🏖️"
        )
    elif month in [9, 10, 11]:
        return (
            "🍂 IssueCoin zbiera huby 🍄, borievky a jablká 🍎 – "
            "vonku je viac dažďa 🌧️, ale nálada zostáva dobrá! ☕"
        )
    return "🙂 IssueCoin je pripravený na tvoje výdavky!"

# Vtipné hlášky
ISSUECOIN_QUOTES = {
    "sk": [
        "💡 Ušetri dnes, potešíš sa zajtra!",
        "💸 Aj drobné sa rátajú – hlavne v piatok večer. 😉",
        "🎉 Nakupuj s rozumom, nie s náladou!",
        "🛒 Tvoj košík je plný, ale aj tvoj život, dúfam! ❤️",
        "😅 Potraviny rastú ako huby po daždi – aj ceny!"
    ],
    "en": [
        "💡 Save today, smile tomorrow!",
        "💸 Every coin counts – especially on Friday nights. 😉",
        "🎉 Shop smart, not emotional!",
        "🛒 Your cart is full – hopefully your heart too! ❤️",
        "😅 Groceries are growing faster than mushrooms!"
    ]
}

def issuecoin_message(lang="sk"):
    mood = get_season_avatar()
    quote = choice(ISSUECOIN_QUOTES.get(lang, ISSUECOIN_QUOTES["sk"]))
    return f"{mood}\n\n{quote}"

# ---------------------------
# COUNTRIES (simplified)
# ---------------------------
COUNTRIES = {
    "sk": ["Česko – CZK Kč", "Slovensko – EUR €", "USA – USD $"],
    "en": ["Czechia – CZK Kč", "Slovakia – EUR €", "USA – USD $"]
}
COUNTRY_TO_CODE = {label: label.split("–")[-1].strip().split()[0] for label in COUNTRIES["sk"] + COUNTRIES["en"]}

# ---------------------------
# STATE INIT
# ---------------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=[
        "Date", "Country", "Currency", "Amount", "Category", "Shop", "Note",
        "Converted_CZK", "Rate_value", "Rate_date"
    ])

# ---------------------------
# CNB HELPERS (TXT feed)
# ---------------------------
@st.cache_data(ttl=600)
def fetch_cnb_txt(date_str: str):
    url = f"https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/daily.txt?date={date_str}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None
    return r.text

def parse_rate_from_txt(txt: str, code: str):
    if not txt:
        return None, None
    lines = txt.splitlines()
    header_date = lines[0].split(" #")[0].strip()
    for line in lines[2:]:
        parts = line.strip().split("|")
        if len(parts) == 5:
            _, _, qty, c_code, rate = parts
            if c_code == code:
                try:
                    return float(rate.replace(",", ".")) / float(qty.replace(",", ".")), header_date
                except:
                    return None, None
    return None, None

def get_rate_for(code: str, d: dt_date):
    txt = fetch_cnb_txt(d.strftime("%d.%m.%Y"))
    rate, date_str = parse_rate_from_txt(txt, code)
    if not rate:
        return 1.0, d.isoformat()
    return rate, datetime.strptime(date_str, "%d.%m.%Y").date().isoformat()

# ---------------------------
# CALENDARIFIC API
# ---------------------------
def check_holiday(api_key: str, country_code="CZ", year=None, month=None, day=None):
    if not api_key:
        return None
    if not year:
        year = datetime.today().year
    url = f"https://calendarific.com/api/v2/holidays?api_key={api_key}&country={country_code}&year={year}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    holidays = r.json().get("response", {}).get("holidays", [])
    for h in holidays:
        if str(h["date"]["datetime"]["year"]) == str(year) and \
           str(h["date"]["datetime"]["month"]) == str(month) and \
           str(h["date"]["datetime"]["day"]) == str(day):
            return h["name"]
    return None

# ---------------------------
# UI HEADER
# ---------------------------
st.title(TEXTS[LANG]["app_title"])
st.caption(TEXTS[LANG]["subtitle"])

# ---------------------------
# INPUT FORM
# ---------------------------
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input(TEXTS[LANG]["date"], value=dt_date.today())
        country = st.selectbox(TEXTS[LANG]["country"], COUNTRIES[LANG])
        category = st.selectbox(TEXTS[LANG]["category"], CATEGORIES[LANG])
    with col2:
        amount = st.number_input(TEXTS[LANG]["amount"], min_value=0.0, step=1.0)
        shop = st.text_input(TEXTS[LANG]["shop"])
        note = st.text_input(TEXTS[LANG]["note"])
    submit = st.form_submit_button(TEXTS[LANG]["save"])

if submit:
    code = COUNTRY_TO_CODE[country]
    per_unit, rate_date = (1.0, d.isoformat()) if code == "CZK" else get_rate_for(code, d)
    if not per_unit:
        st.error(TEXTS[LANG]["rate_err"])
    else:
        converted = round(amount * per_unit, 2)
        new_row = pd.DataFrame([{
            "Date": d.isoformat(),
            "Country": country,
            "Currency": code,
            "Amount": amount,
            "Category": category,
            "Shop": shop,
            "Note": note,
            "Converted_CZK": converted,
            "Rate_value": round(per_unit, 4),
            "Rate_date": rate_date
        }])
        st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_row], ignore_index=True)

        if CALENDARIFIC_API:
            holiday = check_holiday(CALENDARIFIC_API, "CZ", d.year, d.month, d.day)
            if holiday:
                st.success(f"{TEXTS[LANG]['holiday']} {holiday} — uži si deň! 😉")

        st.success(f"{TEXTS[LANG]['saved_ok']} {converted} CZK — "
                   f"{TEXTS[LANG]['rate_info']}: {round(per_unit,4)} CZK/1 {code} "
                   f"({TEXTS[LANG]['rate_from']} {rate_date})")

        st.info(issuecoin_message(LANG))

# ---------------------------
# TABLE + SUMMARY
# ---------------------------
st.subheader(TEXTS[LANG]["list"])
df = st.session_state["expenses"]
st.dataframe(df, use_container_width=True)

if not df.empty:
    st.subheader(TEXTS[LANG]["summary"])
    total = df["Converted_CZK"].sum()
    st.metric(TEXTS[LANG]["total"], f"{total:.2f} CZK")

    grouped = df.groupby("Category")["Converted_CZK"].sum().reset_index()
    chart = (
        alt.Chart(grouped)
        .mark_bar()
        .encode(x=alt.X("Category", sort="-y"), y="Converted_CZK", tooltip=["Category", "Converted_CZK"])
        .properties(width=600, height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(TEXTS[LANG]["export"], csv, f"expenses_{dt_date.today()}.csv", "text/csv")

