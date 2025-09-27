import streamlit as st
import pandas as pd
from datetime import date as dt_date, timedelta
import requests

st.set_page_config(page_title="Výdavkový denník – CZK, EUR, USD, GBP, TRY, RUB", layout="centered")

# --- Funkcia na získanie kurzu z ČNB TXT feedu ---
def get_rate_from_cnb(chosen_date, code):
    base_url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/denni_kurz.txt"
    check_date = chosen_date

    for _ in range(7):  # fallback max 7 dní späť
        url = f"{base_url}?date={dt_date.fromisoformat(check_date).strftime('%d.%m.%Y')}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                lines = resp.text.split("\n")
                if len(lines) > 2:
                    for line in lines[2:]:
                        parts = line.split("|")
                        if len(parts) >= 5 and parts[3] == code:
                            amount = int(parts[2])
                            rate = float(parts[4].replace(",", "."))
                            return rate / amount, dt_date.fromisoformat(check_date).strftime("%Y-%m-%d")
        except Exception:
            pass
        prev_date = dt_date.fromisoformat(check_date) - timedelta(days=1)
        check_date = prev_date.strftime("%Y-%m-%d")

    return None, None

# --- Definícia krajín s menami ---
countries = [
    "Česko / Czechia – CZK Kč",
    "Slovensko / Slovakia – EUR €",
    "Nemecko / Germany – EUR €",
    "Francúzsko / France – EUR €",
    "Španielsko / Spain – EUR €",
    "Taliansko / Italy – EUR €",
    "Chorvátsko / Croatia – EUR €",
    "Holandsko / Netherlands – EUR €",
    "Belgicko / Belgium – EUR €",
    "Fínsko / Finland – EUR €",
    "Grécko / Greece – EUR €",
    "USA / United States – USD $",
    "Dubaj / UAE – AED د.إ (prepočet cez USD)",
    "Kuba / Cuba – CUP (prepočet cez USD)",
    "Argentína / Argentina – ARS (prepočet cez USD)",
    "Thajsko / Thailand – THB ฿ (prepočet cez USD)",
    "Vietnam – VND ₫ (prepočet cez USD)",
    "Veľká Británia / United Kingdom – GBP £",
    "Turecko / Turkey – TRY ₺",
    "Rusko / Russia – RUB ₽ (prepočet cez EUR)"
]

categories = ["Potraviny", "Drogérie", "Doprava", "Reštaurácie a bary", "Zábava"]

# --- Session state ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount",
        "Category", "Note", "Converted_CZK", "Rate_date"
    ])

# --- UI ---
st.title("💸 Výdavkový denník – CZK, EUR, USD, GBP, TRY, RUB")

with st.form("input_form"):
    col1, col2 = st.columns(2)

    with col1:
        purchase_date = st.date_input("📅 Dátum nákupu", value=dt_date.today())
        shop = st.text_input("🏪 Obchod / miesto")
        country_display = st.selectbox("🌍 Krajina + mena", countries)

    with col2:
        amount = st.number_input("💰 Suma", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Kategória", categories)

    note = st.text_input("📝 Poznámka")
    submitted = st.form_submit_button("💾 Uložiť nákup")

    if submitted:
        rate, rate_date = None, None
        currency_code = None

        # --- CZK ---
        if "CZK" in country_display:
            currency_code = "CZK"
            rate, rate_date = 1.0, purchase_date.strftime("%Y-%m-%d")

        # --- EUR ---
        elif "EUR" in country_display and "RUB" not in country_display:
            currency_code = "EUR"
            rate, rate_date = get_rate_from_cnb(purchase_date.strftime("%Y-%m-%d"), "EUR")

        # --- USD (USA + fallback pre Dubaj, Kubu, Argentínu, Thajsko, Vietnam) ---
        elif "USD" in country_display or "AED" in country_display or "CUP" in country_display or "ARS" in country_display or "THB" in country_display or "VND" in country_display:
            if "AED" in country_display:
                st.warning("ℹ️ Dirham (AED) nie je v kurzovom lístku ČNB. Prepočet bude vykonaný podľa kurzu USD.")
            if "CUP" in country_display:
                st.warning("ℹ️ Kubánske peso (CUP) nie je vyhlasované ČNB. Prepočet bude vykonaný podľa kurzu USD.")
            if "ARS" in country_display:
                st.warning("ℹ️ Argentínske peso (ARS) je veľmi nestabilné. Prepočet bude vykonaný podľa kurzu USD.")
            if "THB" in country_display:
                st.warning("ℹ️ Oficiálna mena Thajska je baht (THB). Prepočet bude vykonaný podľa kurzu USD.")
            if "VND" in country_display:
                st.warning("ℹ️ Oficiálna mena Vietnamu je dong (VND). Prepočet bude vykonaný podľa kurzu USD.")

            currency_code = "USD"
            rate, rate_date = get_rate_from_cnb(purchase_date.strftime("%Y-%m-%d"), "USD")

        # --- GBP ---
        elif "GBP" in country_display:
            currency_code = "GBP"
            rate, rate_date = get_rate_from_cnb(purchase_date.strftime("%Y-%m-%d"), "GBP")

        # --- TRY (Turecko) ---
        elif "TRY" in country_display:
            currency_code = "TRY"
            rate, rate_date = get_rate_from_cnb(purchase_date.strftime("%Y-%m-%d"), "TRY")

        # --- RUB (fallback cez EUR) ---
        elif "RUB" in country_display:
            st.warning("ℹ️ Ruský rubeľ (RUB) nie je stabilný. Prepočet bude vykonaný podľa kurzu EUR.")
            currency_code = "RUB (počítané cez EUR)"
            rate, rate_date = get_rate_from_cnb(purchase_date.strftime("%Y-%m-%d"), "EUR")

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
            st.success(f"✅ Nákup pridaný! Prepočet: {converted} CZK (kurz z {rate_date})")
        else:
            st.error(f"❌ Kurz pre {country_display} sa nepodarilo načítať.")

# --- Výpis dát ---
st.subheader("📊 Zoznam nákupov")
st.dataframe(st.session_state.data, use_container_width=True)

if not st.session_state.data.empty:
    st.subheader("📈 Súhrn")
    total = st.session_state.data["Converted_CZK"].sum()
    st.markdown(f"💰 Celkové výdavky: **{total:.2f} CZK**")

st.caption("ℹ️ CZK = vždy 1 CZK. EUR, USD, GBP, TRY = podľa ČNB (TXT feed). "
           "RUB, CUP, AED, ARS, THB, VND = fallback na silnú menu. "
           "Kurzy sa vyhlasujú každý pracovný deň o 14:30. "
           "Ak pre dátum nie sú k dispozícii, použije sa posledný dostupný kurz.")
