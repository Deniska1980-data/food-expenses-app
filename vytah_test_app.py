import os
import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, date as dt_date

# -----------------------------------------------------------------------------
# App config
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Expense Diary", layout="wide")

# -----------------------------------------------------------------------------
# Custom CSS (čitateľnosť)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"]  { font-size: 16px; line-height: 1.6; }
h1 { font-size: 28px !important; }
h2 { font-size: 24px !important; }
h3 { font-size: 20px !important; }
.stButton>button { font-size: 18px; padding: 10px 20px; }
.stSelectbox>div>div { font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Bočný panel: jazyk + (voliteľne) Calendarific API key
# -----------------------------------------------------------------------------
with st.sidebar:
    lang_choice = st.selectbox("🌐 Language / Jazyk", ["Slovensky / Česky", "English"], index=0)
    # pokus o načítanie tajomstva; ak nie je, umožníme vložiť manuálne
    default_key = st.secrets.get("CALENDARIFIC_API_KEY", "")
    api_key_input = st.text_input(
        "🔑 Calendarific API key (optional)",
        value=default_key,
        type="password",
        help="Môžeš ho mať v st.secrets['CALENDARIFIC_API_KEY'] alebo vložiť sem."
    )
    if api_key_input:
        st.session_state["calendarific_api_key"] = api_key_input

LANG = "sk" if "Slovensky" in lang_choice else "en"

# -----------------------------------------------------------------------------
# Preklady
# -----------------------------------------------------------------------------
TEXTS = {
    "sk": {
        "app_title": "💰 Výdavkový denník / Výdajový deník",
        "subtitle": "CZK = vždy 1:1. Ostatné meny podľa denného kurzu ČNB. "
                    "Ak pre vybraný deň nie je kurz, použije sa posledný dostupný kurz. / "
                    "CZK = vždy 1:1. Ostatní měny podle denního kurzu České národní banky. "
                    "Pokud kurz není k dispozici, použije se poslední známý kurz.",
        "date": "📅 Dátum nákupu / Datum nákupu",
        "country": "🌍 Krajina + mena / Měna",
        "amount": "💵 Suma / Částka",
        "category": "📂 Kategória / Kategorie",
        "shop": "🏬 Obchod / miesto / Obchod / místo",
        "note": "📝 Poznámka",
        "save": "💾 Uložiť nákup / Uložit nákup",
        "list": "🧾 Zoznam nákupov / Seznam nákupů",
        "summary": "📊 Súhrn mesačných výdavkov / Souhrn měsíčních výdajů",
        "total": "Celkové výdavky / Celkové výdaje",
        "filter": "🔎 Filter výdavkov / Filtrování výdajů",
        "yr": "Rok", "mo": "Mesiac / Měsíc",
        "rate_err": "❌ Kurz sa nepodarilo načítať. / Kurz se nepodařilo načíst.",
        "saved_ok": "Záznam uložený! / Záznam uložen!",
        "rate_info": "Použitý kurz / Použitý kurz",
        "rate_from": "k / k",
        "export": "💾 Exportovať do CSV",
        "holiday": "🎉 Štátny sviatok / svátek",
        "holiday_note": "Dnes je {name} ({country}) — uži si deň! 😉",
        "no_api_key": "ℹ️ Calendarific: zadaj API kľúč v bočnom paneli, ak chceš sviatky."
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
        "filter": "🔎 Expense filter",
        "yr": "Year", "mo": "Month",
        "rate_err": "❌ Could not fetch exchange rate.",
        "saved_ok": "Saved!",
        "rate_info": "Applied rate",
        "rate_from": "as of",
        "export": "💾 Export CSV",
        "holiday": "🎉 Public holiday",
        "holiday_note": "Today is {name} ({country}) — enjoy the day! 😉",
        "no_api_key": "ℹ️ Calendarific: add API key in the sidebar if you want holidays."
    }
}

CATEGORIES = {
    "sk": [
        "Potraviny 🛒 / Potraviny 🛒",
        "Drogérie 🧴 / Drogérie 🧴",
        "Doprava 🚌 / Doprava 🚌",
        "Reštaurácie a bary 🍽️ / Restaurace a bary 🍽️",
        "Zábava 🎉 / Zábava 🎉",
        "Odevy 👕 / Oblečení 👕",
        "Obuv 👟 / Obuv 👟",
        "Elektronika 💻 / Elektronika 💻",
        "Domácnosť / nábytok 🛋️ / Domácnost / nábytek 🛋️",
        "Šport a voľný čas 🏀 / Sport a volný čas 🏀",
        "Zdravie a lekáreň 💊 / Zdraví a lékárna 💊",
        "Cestovanie / dovolenka ✈️ / Cestování / dovolená ✈️",
        "Vzdelávanie / kurzy 📚 / Vzdělávání / kurzy 📚"
    ],
    "en": [
        "Groceries 🛒",
        "Drugstore 🧴",
        "Transport 🚌",
        "Restaurants & Bars 🍽️",
        "Entertainment 🎉",
        "Clothing 👕",
        "Shoes 👟",
        "Electronics 💻",
        "Household / Furniture 🛋️",
        "Sports & Leisure 🏀",
        "Health & Pharmacy 💊",
        "Travel / Holiday ✈️",
        "Education / Courses 📚"
    ]
}

MESSAGES = {
    "sk": {
        "food": "🍎 Potraviny niečo stoja – pri väčšej rodine je to prirodzené. 😉 / "
                "Potraviny něco stojí – u větší rodiny je to přirozené. 😉",
        "fun": "🎉 Zábavy nikdy nie je dosť! Len pozor, aby ti ešte zostalo aj na chlebík. 😉 / "
               "Zábavy nikdy není dost! Jen pozor, ať ti ještě zbyde i na chleba. 😉",
        "drug": "🧴 Drogéria je drahá, hlavne keď sú v tom deti. 😉 / "
                "Drogérie je drahá, hlavně když jsou v tom děti. 😉",
        "elec": "💻 Nový kúsok? Nech dlho slúži a uľahčí deň. 🚀 / "
                "Nový kousek? Ať dlouho vydrží a usnadní den. 🚀",
    },
    "en": {
        "food": "🍎 Groceries are pricey – with a bigger family, that’s normal. 😉",
        "fun": "🎉 There’s never too much fun! Just keep a little left for bread. 😉",
        "drug": "🧴 Drugstore items can be expensive, especially with kids. You’ve got this. 😉",
        "elec": "💻 New gadget? May it last and make life easier. 🚀",
    }
}

# -----------------------------------------------------------------------------
# Krajiny + meny (labely) a mapovanie -> kód meny (pre ČNB)
# -----------------------------------------------------------------------------
COUNTRIES = {
    "sk": [
        "Česko – CZK Kč",
        "Slovensko – EUR €",
        "Nemecko – EUR € / Německo – EUR €",
        "Rakúsko – EUR € / Rakousko – EUR €",
        "Francúzsko – EUR € / Francie – EUR €",
        "Španielsko – EUR € / Španělsko – EUR €",
        "Taliansko – EUR € / Itálie – EUR €",
        "Holandsko – EUR € / Nizozemsko – EUR €",
        "Belgicko – EUR € / Belgie – EUR €",
        "Fínsko – EUR € / Finsko – EUR €",
        "Írsko – EUR € / Irsko – EUR €",
        "Portugalsko – EUR €",
        "Grécko – EUR € / Řecko – EUR €",
        "Slovinsko – EUR €",
        "Litva – EUR €",
        "Lotyšsko – EUR €",
        "Estónsko – EUR €",
        "Malta – EUR €",
        "Cyprus – EUR €",
        "Chorvátsko – EUR € / Chorvatsko – EUR €",
        "USA – USD $",
        "Veľká Británia – GBP £ / Velká Británie – GBP £",
        "Poľsko – PLN zł / Polsko – PLN zł",
        "Maďarsko – HUF Ft / Maďarsko – HUF Ft",
        "Švajčiarsko – CHF ₣ / Švýcarsko – CHF ₣",
        "Dánsko – DKK kr / Dánsko – DKK kr",
        "Švédsko – SEK kr / Švédsko – SEK kr",
        "Nórsko – NOK kr / Norsko – NOK kr",
        "Kanada – CAD $",
        "Japonsko – JPY ¥"
    ],
    "en": [
        "Czechia – CZK Kč",
        "Slovakia – EUR €",
        "Germany – EUR €",
        "Austria – EUR €",
        "France – EUR €",
        "Spain – EUR €",
        "Italy – EUR €",
        "Netherlands – EUR €",
        "Belgium – EUR €",
        "Finland – EUR €",
        "Ireland – EUR €",
        "Portugal – EUR €",
        "Greece – EUR €",
        "Slovenia – EUR €",
        "Lithuania – EUR €",
        "Latvia – EUR €",
        "Estonia – EUR €",
        "Malta – EUR €",
        "Cyprus – EUR €",
        "Croatia – EUR €",
        "USA – USD $",
        "United Kingdom – GBP £",
        "Poland – PLN zł",
        "Hungary – HUF Ft",
        "Switzerland – CHF ₣",
        "Denmark – DKK kr",
        "Sweden – SEK kr",
        "Norway – NOK kr",
        "Canada – CAD $",
        "Japan – JPY ¥"
    ]
}

COUNTRY_TO_CODE = {}
for label in COUNTRIES["sk"] + COUNTRIES["en"]:
    code = label.split("–")[-1].strip().split()[0]
    COUNTRY_TO_CODE[label] = code

# Mapovanie krajiny -> ISO2 pre Calendarific
COUNTRY_TO_ISO2 = {
    "Česko – CZK Kč": "CZ", "Czechia – CZK Kč": "CZ",
    "Slovensko – EUR €": "SK", "Slovakia – EUR €": "SK",
    "Nemecko – EUR € / Německo – EUR €": "DE", "Germany – EUR €": "DE",
    "Rakúsko – EUR € / Rakousko – EUR €": "AT", "Austria – EUR €": "AT",
    "USA – USD $": "US", "United Kingdom – GBP £": "GB",
    "Veľká Británia – GBP £ / Velká Británie – GBP £": "GB",
    "Poľsko – PLN zł / Polsko – PLN zł": "PL", "Hungary – HUF Ft": "HU",
    "Maďarsko – HUF Ft / Maďarsko – HUF Ft": "HU",
    "Švajčiarsko – CHF ₣ / Švýcarsko – CHF ₣": "CH",
    "Japonsko – JPY ¥": "JP",
    # Európske krajiny s EUR – Calendarific akceptuje ISO2:
    "Francúzsko – EUR € / Francie – EUR €":"FR","France – EUR €":"FR",
    "Španielsko – EUR € / Španělsko – EUR €":"ES","Spain – EUR €":"ES",
    "Taliansko – EUR € / Itálie – EUR €":"IT","Italy – EUR €":"IT",
    "Holandsko – EUR € / Nizozemsko – EUR €":"NL","Netherlands – EUR €":"NL",
    "Belgicko – EUR € / Belgie – EUR €":"BE","Belgium – EUR €":"BE",
    "Fínsko – EUR € / Finsko – EUR €":"FI","Finland – EUR €":"FI",
    "Írsko – EUR € / Irsko – EUR €":"IE","Ireland – EUR €":"IE",
    "Portugalsko – EUR €":"PT","Portugal – EUR €":"PT",
    "Grécko – EUR € / Řecko – EUR €":"GR","Greece – EUR €":"GR",
    "Slovinsko – EUR €":"SI","Slovenia – EUR €":"SI",
    "Litva – EUR €":"LT","Lithuania – EUR €":"LT",
    "Lotyšsko – EUR €":"LV","Latvia – EUR €":"LV",
    "Estónsko – EUR €":"EE","Estonia – EUR €":"EE",
    "Malta – EUR €":"MT","Malta – EUR €":"MT",
    "Cyprus – EUR €":"CY","Cyprus – EUR €":"CY",
    "Chorvátsko – EUR € / Chorvatsko – EUR €":"HR","Croatia – EUR €":"HR",
    "Dánsko – DKK kr / Dánsko – DKK kr":"DK","Denmark – DKK kr":"DK",
    "Švédsko – SEK kr / Švédsko – SEK kr":"SE","Sweden – SEK kr":"SE",
    "Nórsko – NOK kr / Norsko – NOK kr":"NO","Norway – NOK kr":"NO",
    "Kanada – CAD $":"CA","Canada – CAD $":"CA",
    "Švajčiarsko – CHF ₣ / Švýcarsko – CHF ₣":"CH","Switzerland – CHF ₣":"CH",
}

# -----------------------------------------------------------------------------
# Stav (tabuľka výdavkov)
# -----------------------------------------------------------------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=[
        "Date","Country","Currency","Amount","Category","Shop","Note",
        "Converted_CZK","Rate_value","Rate_date"
    ])

# -----------------------------------------------------------------------------
# ČNB TXT feed (kurzy)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600)
def fetch_cnb_txt(date_str: str):
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date_str}"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None
    return r.text

@st.cache_data(ttl=600)
def fetch_cnb_txt_latest():
    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return None
    return r.text

def parse_rate_from_txt(txt: str, code: str):
    if not txt: return None, None, None
    lines = txt.splitlines()
    header_date = lines[0].split(" #")[0].strip() if lines else None
    for line in lines[2:]:
        parts = line.strip().split("|")
        if len(parts) == 5:
            _, _, qty, c_code, rate = parts
            if c_code == code:
                try:
                    qty_f = float(qty.replace(",", "."))
                    rate_f = float(rate.replace(",", "."))
                    return rate_f, qty_f, header_date
                except:
                    return None, None, header_date
    return None, None, header_date

def get_rate_for(code: str, d: dt_date):
    d_str = d.strftime("%d.%m.%Y")
    txt = fetch_cnb_txt(d_str)
    rate, qty, header_date = parse_rate_from_txt(txt, code)
    if rate is None:
        txt2 = fetch_cnb_txt_latest()
        rate, qty, header_date = parse_rate_from_txt(txt2, code)
        rate_date_iso = datetime.today().date().isoformat()
    else:
        rate_date_iso = datetime.strptime(header_date, "%d.%m.%Y").date().isoformat()
    if rate is None or not qty:
        return None, None
    return rate/qty, rate_date_iso

# -----------------------------------------------------------------------------
# Calendarific – sviatky (voliteľné)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def get_holiday_name(api_key: str, country_iso2: str, d: dt_date):
    """Vráti názov sviatku (alebo None) pre daný dátum/krajinu."""
    if not api_key or not country_iso2:
        return None
    url = "https://calendarific.com/api/v2/holidays"
    params = {
        "api_key": api_key,
        "country": country_iso2,
        "year": d.year,
        "day": d.day,
        "month": d.month
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        holidays = data.get("response", {}).get("holidays", [])
        # prednosť národným sviatkom
        for h in holidays:
            types = h.get("type", [])
            if any("National" in t for t in types):
                return h.get("name")
        # inak zober prvý
        if holidays:
            return holidays[0].get("name")
    except Exception:
        return None
    return None

def calendarific_api_key():
    return st.session_state.get("calendarific_api_key") or os.environ.get("CALENDARIFIC_API_KEY") or st.secrets.get("CALENDARIFIC_API_KEY")

# -----------------------------------------------------------------------------
# UI header
# -----------------------------------------------------------------------------
st.title(TEXTS[LANG]["app_title"])
st.caption(TEXTS[LANG]["subtitle"])

# -----------------------------------------------------------------------------
# Vstupný formulár
# -----------------------------------------------------------------------------
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input(TEXTS[LANG]["date"], value=dt_date.today(), min_value=dt_date(2024,1,1))
        country = st.selectbox(TEXTS[LANG]["country"], COUNTRIES[LANG])
        category = st.selectbox(TEXTS[LANG]["category"], CATEGORIES[LANG])
    with col2:
        amount = st.number_input(TEXTS[LANG]["amount"], min_value=0.0, step=1.0)
        shop = st.text_input(TEXTS[LANG]["shop"])
        note = st.text_input(TEXTS[LANG]["note"])
    submit = st.form_submit_button(TEXTS[LANG]["save"])

# -----------------------------------------------------------------------------
# Uloženie + hlášky (ISU/COIN štýl) + sviatky + konverzia
# -----------------------------------------------------------------------------
if submit:
    code = COUNTRY_TO_CODE[country]
    per_unit, rate_date = (1.0, d.isoformat()) if code == "CZK" else get_rate_for(code, d)

    # Calendarific (ak je kľúč)
    api_key = calendarific_api_key()
    if not api_key:
        st.info(TEXTS[LANG]["no_api_key"])
    else:
        iso2 = COUNTRY_TO_ISO2.get(country)
        hol = get_holiday_name(api_key, iso2, d)
        if hol:
            st.success(f"🎉 {TEXTS[LANG]['holiday']}: " +
                       TEXTS[LANG]["holiday_note"].format(name=hol, country=iso2))

    if per_unit is None:
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

        st.success(
            f"{TEXTS[LANG]['saved_ok']} {converted} CZK — "
            f"{TEXTS[LANG]['rate_info']}: {round(per_unit,4)} CZK/1 {code} "
            f"({TEXTS[LANG]['rate_from']} {rate_date})"
        )

        # “ISU/COIN” (ľahké pravidlá + vtipné RAG tipy)
        sums = st.session_state["expenses"].groupby("Category")["Converted_CZK"].sum()

        # prahy podľa kategórií
        if any(k in sums.index and sums[k] > 6000 for k in ["Potraviny 🛒 / Potraviny 🛒", "Groceries 🛒"]):
            st.info(MESSAGES[LANG]["food"])
        if any(k in sums.index and sums[k] > 2000 for k in ["Zábava 🎉 / Zábava 🎉", "Entertainment 🎉"]):
            st.warning(MESSAGES[LANG]["fun"])
        if any(k in sums.index and sums[k] > 2000 for k in ["Drogérie 🧴 / Drogérie 🧴", "Drugstore 🧴"]):
            st.info(MESSAGES[LANG]["drug"])
        if any(k in sums.index and sums[k] > 8000 for k in ["Elektronika 💻 / Elektronika 💻", "Electronics 💻"]):
            st.info(MESSAGES[LANG]["elec"])

        # drobný “RAG” tip podľa dňa v týždni + kategórie
        weekday = d.weekday()  # 0=Mon ... 6=Sun
        if weekday in (5, 6) and ("Restaur" in category or "Reštaur" in category or "Restaurants" in category):
            st.info("🍽️ Weekend treat is fine — set a small cap so Monday isn’t shocked. 😉")
        if "Travel" in category or "Cestovanie" in category:
            st.info("✈️ Travel purchase logged. Tip: keep receipts in Note for easier export later.")

# -----------------------------------------------------------------------------
# Zoznam + súhrn + graf
# -----------------------------------------------------------------------------
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
        .encode(
            x=alt.X("Category", sort="-y", title=TEXTS[LANG]["category"]),
            y=alt.Y("Converted_CZK", title="CZK"),
            tooltip=["Category", "Converted_CZK"]
        )
        .properties(width=600, height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    # Export CSV
    csv = df.to_csv(index=False).encode("utf-8")
    file_name = f"expenses_{dt_date.today().isoformat()}.csv"
    st.download_button(
        label=TEXTS[LANG]["export"],
        data=csv,
        file_name=file_name,
        mime="text/csv",
    )
