# app.py
import os
import json
import time
from datetime import datetime, date as dt_date

import streamlit as st
import pandas as pd
import requests
import altair as alt

# ---------------------------
# Page & global config
# ---------------------------
st.set_page_config(page_title="Expense Diary + Titan-ready", layout="wide")

# ---------------------------
# Sidebar: Debug toggle
# ---------------------------
with st.sidebar:
    st.header("⚙️ Nastavenia")
    show_debug = st.checkbox("Zobraziť debug panel", value=False, help="Zobrazí stav CNB/Calendarific/Titan volaní.")
    st.markdown("---")
    st.caption("🧠 Titan je *pasívny*, kým nenastavíš ENV:\n- ENABLE_TITAN=1\n- BEDROCK_REGION (napr. eu-central-1)\n- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")

# ---------------------------
# Session debug store
# ---------------------------
if "DEBUG" not in st.session_state:
    st.session_state.DEBUG = {
        "cnb": {"ok": None, "msg": "", "ts": None},
        "calendarific": {"ok": None, "msg": "", "ts": None},
        "titan": {"ok": None, "msg": "", "ts": None, "last_hint": None},
    }

def _debug_set(section: str, ok: bool, msg: str, extra=None):
    st.session_state.DEBUG[section]["ok"] = ok
    st.session_state.DEBUG[section]["msg"] = msg
    st.session_state.DEBUG[section]["ts"] = datetime.now().strftime("%H:%M:%S")
    if section == "titan" and extra is not None:
        st.session_state.DEBUG[section]["last_hint"] = extra

# ---------------------------
# Custom CSS (readability + colored badges)
# ---------------------------
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 16px; line-height: 1.6; }
    h1 { font-size: 28px !important; } h2 { font-size: 24px !important; } h3 { font-size: 20px !important; }
    .stButton>button { font-size: 18px; padding: 10px 20px; }
    .stSelectbox>div>div { font-size: 16px; }
    .badge-ok {background:#16a34a; color:white; padding:2px 8px; border-radius:999px; font-size:12px;}
    .badge-warn {background:#ca8a04; color:white; padding:2px 8px; border-radius:999px; font-size:12px;}
    .badge-err {background:#dc2626; color:white; padding:2px 8px; border-radius:999px; font-size:12px;}
    .badge-off {background:#6b7280; color:white; padding:2px 8px; border-radius:999px; font-size:12px;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# Language switch
# ---------------------------
left, right = st.columns([7, 3])
with right:
    lang_choice = st.selectbox("🌐 Language / Jazyk", ["Slovensky / Česky", "English"], index=0)
LANG = "sk" if "Slovensky" in lang_choice else "en"

# ---------------------------
# Translations
# ---------------------------
TEXTS = {
    "sk": {
        "app_title": "💰 Výdavkový denník / Výdajový deník + Titan-ready",
        "subtitle": "CZK = vždy 1:1. Ostatné meny podľa denného kurzu ČNB (TXT feed). "
                    "Ak pre vybraný deň nie je kurz, použije sa posledný dostupný kurz. "
                    "Sviatky z Calendarific. Titan hlášky po aktivácii.",
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
        "yr": "Rok",
        "mo": "Mesiac / Měsíc",
        "rate_err": "❌ Kurz sa nepodarilo načítať (CNB TXT).",
        "saved_ok": "Záznam uložený! / Záznam uložen!",
        "rate_info": "Použitý kurz",
        "rate_from": "k",
        "export": "💾 Exportovať do CSV",
        "holiday_msg": "🎌 Dnes je štátny sviatok ({name}) – uži deň s rozumom!",
        "titan_off": "🧠 Titan: vypnutý (ENABLE_TITAN!=1 alebo bez AWS nastavení)."
    },
    "en": {
        "app_title": "💰 Expense Diary + Titan-ready",
        "subtitle": "CZK = always 1:1. Other currencies follow CNB daily TXT feed. "
                    "If no rate is available for the selected date, the last available rate is used. "
                    "Holidays via Calendarific. Titan messages once enabled.",
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
        "yr": "Year",
        "mo": "Month",
        "rate_err": "❌ Could not fetch exchange rate (CNB TXT).",
        "saved_ok": "Saved!",
        "rate_info": "Applied rate",
        "rate_from": "as of",
        "export": "💾 Export CSV",
        "holiday_msg": "🎌 Today is a public holiday ({name}) – enjoy wisely!",
        "titan_off": "🧠 Titan: disabled (ENABLE_TITAN!=1 or missing AWS settings)."
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
        "food": "🍎 Potraviny niečo stoja – pri väčšej rodine je to prirodzené. 😉",
        "fun": "🎉 Zábavy nikdy nie je dosť! Len pozor, aby ti ešte zostalo aj na chlebík. 😉",
        "drug": "🧴 Drogéria je drahá, hlavne keď sú v tom deti. 😉",
        "elec": "💻 Nový kúsok? Nech dlho slúži a uľahčí deň. 🚀",
    },
    "en": {
        "food": "🍎 Groceries are pricey – with a bigger family, that’s normal. 😉",
        "fun": "🎉 There’s never too much fun! Just keep a little left for bread. 😉",
        "drug": "🧴 Drugstore items can be expensive, especially with kids. You’ve got this. 😉",
        "elec": "💻 New gadget? May it last and make life easier. 🚀",
    }
}

# ---------------------------
# Countries + currencies
# ---------------------------
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

# ---------------------------
# State init
# ---------------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = pd.DataFrame(columns=[
        "Date", "Country", "Currency", "Amount", "Category", "Shop", "Note",
        "Converted_CZK", "Rate_value", "Rate_date"
    ])

# ---------------------------
# CNB TXT feed helpers
# ---------------------------
@st.cache_data(ttl=600)
def fetch_cnb_txt(date_str: str):
    # CNB TXT daily file with ?date=DD.MM.YYYY
    url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date_str}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            _debug_set("cnb", False, f"HTTP {r.status_code} @ {url}")
            return None
        return r.text
    except Exception as e:
        _debug_set("cnb", False, f"Exception: {e}")
        return None

@st.cache_data(ttl=600)
def fetch_cnb_txt_latest():
    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trru/kurzy-devizoveho-trhu/denni_kurz.txt"
    # NB: original long path typo-proofing; use official canonical:
    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            _debug_set("cnb", False, f"HTTP {r.status_code} (latest) @ {url}")
            return None
        return r.text
    except Exception as e:
        _debug_set("cnb", False, f"Exception (latest): {e}")
        return None

def parse_rate_from_txt(txt: str, code: str):
    if not txt:
        return None, None, None
    lines = txt.splitlines()
    header_date = lines[0].split(" #")[0].strip() if lines else None
    for line in lines[2:]:
        parts = line.strip().split("|")
        # Format: Country|Currency|Amount|Code|Rate
        if len(parts) == 5:
            _, _, qty, c_code, rate = parts
            if c_code == code:
                try:
                    qty_f = float(qty.replace(",", "."))
                    rate_f = float(rate.replace(",", "."))
                    return rate_f, qty_f, header_date
                except Exception:
                    return None, None, header_date
    return None, None, header_date

def get_rate_for(code: str, d: dt_date):
    if code == "CZK":
        _debug_set("cnb", True, "CZK=1.0 (no fetch)")
        return 1.0, d.isoformat()
    d_str = d.strftime("%d.%m.%Y")
    txt = fetch_cnb_txt(d_str)
    rate, qty, header_date = parse_rate_from_txt(txt, code)
    if rate is None:
        # fallback: latest
        txt2 = fetch_cnb_txt_latest()
        rate, qty, header_date = parse_rate_from_txt(txt2, code)
        rate_date_iso = datetime.today().date().isoformat()
        if rate is None:
            _debug_set("cnb", False, f"No rate for {code} on {d_str} nor latest")
            return None, None
        _debug_set("cnb", True, f"Used latest TXT for {code}")
    else:
        try:
            rate_date_iso = datetime.strptime(header_date, "%d.%m.%Y").date().isoformat()
        except Exception:
            rate_date_iso = d.isoformat()
        _debug_set("cnb", True, f"Used day TXT for {code}")
    return rate/qty, rate_date_iso

# ---------------------------
# Calendarific (holidays)
# ---------------------------
CALENDARIFIC_API_KEY = os.getenv("CALENDARIFIC_API_KEY", "").strip()

@st.cache_data(ttl=3600)
def calendarific_holidays(country_code: str, year: int, month: int, day: int):
    if not CALENDARIFIC_API_KEY:
        _debug_set("calendarific", False, "Missing CALENDARIFIC_API_KEY")
        return []
    url = ("https://calendarific.com/api/v2/holidays"
           f"?&api_key={CALENDARIFIC_API_KEY}"
           f"&country={country_code}&year={year}&month={month}&day={day}")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            _debug_set("calendarific", False, f"HTTP {r.status_code}")
            return []
        data = r.json()
        hols = data.get("response", {}).get("holidays", [])
        _debug_set("calendarific", True, f"{len(hols)} holiday(s) @ {country_code}")
        return hols
    except Exception as e:
        _debug_set("calendarific", False, f"Exception: {e}")
        return []

def resolve_country_for_calendarific(country_label: str):
    # very small mapping: CZ, SK else EU pick CZ as default
    if "Česko" in country_label or "Czech" in country_label:
        return "CZ"
    if "Slovensko" in country_label or "Slovakia" in country_label:
        return "SK"
    # fallback: try code by currency (EUR-heavy -> SK as example)
    return "CZ"

# ---------------------------
# Titan (AWS Bedrock) – optional brain
# ---------------------------
def titan_enabled() -> bool:
    return os.getenv("ENABLE_TITAN", "0") == "1" and bool(os.getenv("BEDROCK_REGION"))

def titan_hint(context: dict) -> str | None:
    """
    Returns a short, fun hint text from Titan (when enabled). Otherwise None.
    """
    if not titan_enabled():
        _debug_set("titan", False, "Titan disabled")
        return None
    try:
        import boto3
        region = os.getenv("BEDROCK_REGION")
        model_id = os.getenv("TITAN_MODEL_ID", "amazon.titan-text-lite-v1")  # safe default

        client = boto3.client("bedrock-runtime", region_name=region)
        prompt = (
            "You are a playful finance assistant. Based on this JSON purchase context, "
            "return ONE short motivational/funny sentence in the same language as 'lang'. "
            "Keep it <140 chars.\n\n"
            f"{json.dumps(context, ensure_ascii=False)}"
        )

        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 80,
                "temperature": 0.6,
                "topP": 0.9
            }
        })
        resp = client.invoke_model(
            modelId=model_id,
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        payload = json.loads(resp.get("body").read().decode("utf-8"))
        out = payload.get("results", [{}])[0].get("outputText", "").strip()
        out = out.replace("\n", " ").strip()
        if out:
            _debug_set("titan", True, "OK", extra=out)
            return out
        _debug_set("titan", False, "Empty result")
        return None
    except Exception as e:
        _debug_set("titan", False, f"Exception: {e}")
        return None

# ---------------------------
# UI header
# ---------------------------
st.title(TEXTS[LANG]["app_title"])
st.caption(TEXTS[LANG]["subtitle"])

# ---------------------------
# Input form
# ---------------------------
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

# ---------------------------
# Handle submit
# ---------------------------
if submit:
    code = COUNTRY_TO_CODE[country]
    per_unit, rate_date = get_rate_for(code, d)
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

        # 1) Static IssueCoin/EAG style messages (thresholds)
        df_now = st.session_state["expenses"]
        sums = df_now.groupby("Category")["Converted_CZK"].sum() if not df_now.empty else pd.Series(dtype=float)
        if any(k in sums.index and sums[k] > 6000 for k in ["Potraviny 🛒 / Potraviny 🛒", "Groceries 🛒"]):
            st.info(MESSAGES[LANG]["food"])
        if any(k in sums.index and sums[k] > 2000 for k in ["Zábava 🎉 / Zábava 🎉", "Entertainment 🎉"]):
            st.warning(MESSAGES[LANG]["fun"])
        if any(k in sums.index and sums[k] > 2000 for k in ["Drogérie 🧴 / Drogérie 🧴", "Drugstore 🧴"]):
            st.info(MESSAGES[LANG]["drug"])
        if "Elektronika" in category or "Electronics" in category:
            st.info(MESSAGES[LANG]["elec"])

        # 2) Holiday hint (Calendarific)
        cc = resolve_country_for_calendarific(country)
        hols = calendarific_holidays(cc, d.year, d.month, d.day)
        if hols:
            name = hols[0].get("name", "Holiday")
            st.warning(TEXTS[LANG]["holiday_msg"].format(name=name))

        # 3) Titan (optional brain)
        context = {
            "lang": LANG,
            "date": d.isoformat(),
            "country": country,
            "currency": code,
            "amount": amount,
            "category": category,
            "shop": shop,
            "note": note,
            "converted_czk": converted
        }
        hint = titan_hint(context)
        if hint:
            st.success(f"🧠 Titan: {hint}")
        else:
            st.caption(TEXTS[LANG]["titan_off"])

# ---------------------------
# List + summary
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

# ---------------------------
# Debug panel (colored status)
# ---------------------------
def badge(section: str):
    it = st.session_state.DEBUG[section]
    ok = it["ok"]
    ts = it["ts"] or "--:--:--"
    msg = it["msg"] or ""
    if ok is None:
        cls, label = "badge-off", "OFF"
    elif ok:
        cls, label = "badge-ok", "OK"
    else:
        cls, label = "badge-err", "ERR"
    st.markdown(f'<span class="{cls}">{label}</span> <small>{ts}</small> — {msg}', unsafe_allow_html=True)

if show_debug:
    st.markdown("### 🧪 Debug panel")
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("**CNB TXT**")
        badge("cnb")
    with colB:
        st.markdown("**Calendarific**")
        badge("calendarific")
    with colC:
        st.markdown("**Titan (Bedrock)**")
        badge("titan")
        last_hint = st.session_state.DEBUG["titan"].get("last_hint")
        if last_hint:
            st.code(last_hint)

