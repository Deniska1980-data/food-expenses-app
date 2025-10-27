# app.py
# -----------------------------------------
# Expense Diary + CNB rates + Titan (AWS Bedrock) "sleep-ready"
# -----------------------------------------
# Titan AI hlášky sa automaticky zapnú, keď:
#  - máš nastavené AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (a ideálne BEDROCK_REGION)
#  - alebo nastavíš AI_ENABLE=1 a bežíš v prostredí, kde je nakonf. AWS (napr. EC2/role)
#
# Závislosti (v requirements.txt):
# streamlit
# pandas
# requests
# altair
# boto3             # (voliteľné – ak nechceš Titan, môže ostať, ale nevolá sa)
#
# Poznámka k regiónu Bedrock:
#  - S3 môže byť v eu-north-1 (Stockholm), no Bedrock je dostupný len v vybraných regiónoch.
#  - Odporúčam: eu-central-1 (Frankfurt) alebo iný podporovaný región.
# -----------------------------------------

import os
import json
import streamlit as st
import pandas as pd
import requests
import altair as alt
from datetime import datetime, date as dt_date

# ---------------------------
# Optional: AWS Bedrock (Titan) klient
# ---------------------------
def _bedrock_available() -> bool:
    # Zapni AI ak je explicitne povolené, alebo nájdené AWS credsi
    if os.environ.get("AI_ENABLE", "").strip() == "1":
        return True
    has_keys = bool(os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))
    return has_keys

_bedrock_client = None
def _init_bedrock_client():
    """Lazy init bedrock-runtime klienta. Bez credov len vráti None."""
    global _bedrock_client
    if _bedrock_client is not None:
        return _bedrock_client
    if not _bedrock_available():
        return None
    try:
        import boto3  # importujeme až tu, nech app beží aj bez boto3
        region = os.environ.get("BEDROCK_REGION", "eu-central-1")  # uprav podľa dostupnosti
        _bedrock_client = boto3.client("bedrock-runtime", region_name=region)
        return _bedrock_client
    except Exception:
        return None

def titan_generate(prompt: str, max_tokens: int = 180) -> str | None:
    """
    Zavolá Titan Text (cez Bedrock) a vráti krátku hlášku alebo None.
    Model ID odporúčané: 'amazon.titan-text-express-v1' alebo 'amazon.titan-text-premier-v1:0'
    (v závislosti od dostupnosti v tvojom regióne/účte).
    """
    client = _init_bedrock_client()
    if client is None:
        return None

    # Skús model priority -> fallback
    model_candidates = [
        "amazon.titan-text-premier-v1:0",
        "amazon.titan-text-express-v1"
    ]

    body_template = lambda text: json.dumps({
        "inputText": text,
        "textGenerationConfig": {
            "maxTokenCount": max_tokens,
            "temperature": 0.6,
            "topP": 0.9,
            "stopSequences": []
        }
    })

    for model_id in model_candidates:
        try:
            resp = client.invoke_model(
                modelId=model_id,
                body=body_template(prompt),
                contentType="application/json",
                accept="application/json"
            )
            payload = json.loads(resp.get("body").read())
            # Titan text responses: {"results":[{"outputText":"..."}]}
            results = payload.get("results") or []
            if results and "outputText" in results[0]:
                text = results[0]["outputText"].strip()
                # Skráť príliš dlhé odpovede (bezpečná poistka)
                return text[:800]
        except Exception:
            # Vyskúšaj ďalší model
            continue
    return None


# ---------------------------
# Streamlit UI setup
# ---------------------------
st.set_page_config(page_title="Expense Diary", layout="wide")

# ---------------------------
# Custom CSS for readability
# ---------------------------
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-size: 16px;  
        line-height: 1.6;
    }
    h1 { font-size: 28px !important; }
    h2 { font-size: 24px !important; }
    h3 { font-size: 20px !important; }
    .stButton>button {
        font-size: 18px;
        padding: 10px 20px;
    }
    .stSelectbox>div>div {
        font-size: 16px;
    }
    .ai-badge {
        display:inline-block;
        padding:2px 8px;
        border-radius:6px;
        background:#f0f2f6;
        font-size:12px;
        margin-left:6px;
    }
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
        "yr": "Rok",
        "mo": "Mesiac / Měsíc",
        "rate_err": "❌ Kurz sa nepodarilo načítať. / Kurz se nepodařilo načíst.",
        "saved_ok": "Záznam uložený! / Záznam uložen!",
        "rate_info": "Použitý kurz / Použitý kurz",
        "rate_from": "k / k",
        "export": "💾 Exportovať do CSV",
        "ai_summary": "🤖 Požiadať Titana o krátky insight",
        "ai_off": "AI spánok: Titan je pripravený, zapne sa po pridaní AWS kľúčov.",
        "ai_on": "AI zapnuté (Titan)",
        "ai_tip_title": "💡 AI tip",
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
        "yr": "Year",
        "mo": "Month",
        "rate_err": "❌ Could not fetch exchange rate.",
        "saved_ok": "Saved!",
        "rate_info": "Applied rate",
        "rate_from": "as of",
        "export": "💾 Export CSV",
        "ai_summary": "🤖 Ask Titan for a quick insight",
        "ai_off": "AI is sleeping: Titan will wake after you add AWS credentials.",
        "ai_on": "AI enabled (Titan)",
        "ai_tip_title": "💡 AI tip",
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

# ---------------------------
# UI header
# ---------------------------
ai_on = _bedrock_available() and _init_bedrock_client() is not None
badge = f'<span class="ai-badge">{"✅ " + TEXTS[LANG]["ai_on"] if ai_on else "💤 " + TEXTS[LANG]["ai_off"]}</span>'
st.title(TEXTS[LANG]["app_title"])
st.caption(TEXTS[LANG]["subtitle"] + " " + badge, unsafe_allow_html=True)

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

if submit:
    code = COUNTRY_TO_CODE[country]
    per_unit, rate_date = (1.0, d.isoformat()) if code == "CZK" else get_rate_for(code, d)
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
        st.success(f"{TEXTS[LANG]['saved_ok']} {converted} CZK "
                   f"— {TEXTS[LANG]['rate_info']}: {round(per_unit,4)} CZK/1 {code} "
                   f"({TEXTS[LANG]['rate_from']} {rate_date})")

        # Pôvodné "IssueCoin" štýlové hlášky podľa sumy a kategórie
        sums = st.session_state["expenses"].groupby("Category")["Converted_CZK"].sum()

        if any(k in sums.index and sums[k] > 6000 for k in ["Potraviny 🛒 / Potraviny 🛒", "Groceries 🛒"]):
            st.info(MESSAGES[LANG]["food"])
        if any(k in sums.index and sums[k] > 2000 for k in ["Zábava 🎉 / Zábava 🎉", "Entertainment 🎉"]):
            st.warning(MESSAGES[LANG]["fun"])
        if any(k in sums.index and sums[k] > 2000 for k in ["Drogérie 🧴 / Drogérie 🧴", "Drugstore 🧴"]):
            st.info(MESSAGES[LANG]["drug"])

        # Titan “mozog”: krátka kontextová hláška (ak je dostupný)
        if ai_on:
            # poskytneme kontext – posledný záznam + top kategórie
            df_tmp = st.session_state["expenses"]
            top = (
                df_tmp.groupby("Category")["Converted_CZK"].sum()
                .sort_values(ascending=False)
                .head(3)
                .to_dict()
            )
            lang_tag = "SK/CZ" if LANG == "sk" else "EN"
            prompt = (
                f"You are a friendly personal finance assistant. Language: {lang_tag}. "
                f"User just saved a purchase.\n"
                f"Last item: date={d.isoformat()}, amount={amount} {code} (~{converted} CZK), "
                f"category={category}, shop={shop or '-'}.\n"
                f"Top categories CZK totals: {top}.\n"
                f"Task: Return ONE short, upbeat line with a tiny tip or witty remark. "
                f"Keep it max ~25 words. If SK/CZ, write in SK/CZ style."
            )
            ai_msg = titan_generate(prompt)
            if ai_msg:
                st.info(f"**{TEXTS[LANG]['ai_tip_title']}:** {ai_msg}")

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

    # ---------------------------
    # Export CSV (local download)
    # ---------------------------
    csv = df.to_csv(index=False).encode("utf-8")
    file_name = f"expenses_{dt_date.today().isoformat()}.csv"
    st.download_button(
        label=TEXTS[LANG]["export"],
        data=csv,
        file_name=file_name,
        mime="text/csv",
    )

    # Voliteľné: jednorazový AI insight nad celým datasetom
    if ai_on:
        if st.button(TEXTS[LANG]["ai_summary"]):
            # Zoberieme malé agregáty ako kontext
            by_month = (
                df.assign(ym=df["Date"].str.slice(0,7))
                  .groupby("ym")["Converted_CZK"]
                  .sum()
                  .sort_index()
                  .tail(6)
                  .to_dict()
            )
            top_cat = (
                df.groupby("Category")["Converted_CZK"]
                  .sum()
                  .sort_values(ascending=False)
                  .head(5)
                  .to_dict()
            )
            lang_tag = "SK/CZ" if LANG == "sk" else "EN"
            prompt = (
                f"You are a concise finance analyst. Language: {lang_tag}. "
                f"Recent 6 months totals CZK: {by_month}. Top 5 categories CZK: {top_cat}. "
                f"Task: Give 2 short bullet tips (~15 words each) to optimize spending. "
                f"If SK/CZ, write in SK/CZ. Be positive and practical."
            )
            ai_msg = titan_generate(prompt, max_tokens=180)
            if ai_msg:
                st.success(ai_msg)
