import streamlit as st
import pandas as pd
from datetime import date as dt_date

st.set_page_config(page_title="My Monthly Expense Diary", layout="centered")
st.title("💸 My Monthly Expense Diary")

st.markdown("Record your purchases and expenses – keep track, even on vacation ☀️")

# --- Initialize DataFrame ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Converted_CZK"
    ])

# --- Input Form ---
st.subheader("➕ Add Purchase")

with st.form("input_form"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("📅 Date", value=dt_date.today())
        shop = st.text_input("🏪 Shop")
        country = st.selectbox("🌍 Country", ["Czechia", "Slovakia", "Croatia", "Other"])

    with col2:
        currency = st.selectbox("💱 Currency", [
            "CZK (Czech koruna)", 
            "EUR (Euro)", 
            "USD (US Dollar)", 
            "GBP (British Pound)"
        ])
        amount = st.number_input("💰 Amount", min_value=0.0, step=0.5)
        category = st.selectbox("📂 Category", ["Food", "Drugstore", "Transport", "Restaurants & Bars", "Entertainment"])

    note = st.text_input("📝 Note (e.g. shampoo, beer in bar...)")
    submitted = st.form_submit_button("💾 Save purchase")

    # 🔹 Temporary fixed exchange rates (later: CNB API)
    if currency.startswith("EUR"):
        rate = 25.0
    elif currency.startswith("USD"):
        rate = 20.0
    elif currency.startswith("GBP"):
        rate = 30.0
    else:
        rate = 1.0

    if submitted:
        converted = amount * rate
        new_record = {
            "Date": date,
            "Shop": shop,
            "Country": country,
            "Currency": currency,
            "Amount": amount,
            "Category": category,
            "Note": note,
            "Converted_CZK": round(converted, 2)
        }
        st.session_state.data = pd.concat(
            [st.session_state.data, pd.DataFrame([new_record])],
            ignore_index=True
        )
        st.success("✅ Purchase has been added!")

# --- Display Table ---
st.subheader("📊 List of Purchases")
st.dataframe(st.session_state.data, use_container_width=True)

# --- Calculations ---
st.subheader("📈 Monthly Expense Summary")

data = st.session_state.data

if not data.empty:
    total_sum = data["Converted_CZK"].sum()
    category_summary = data.groupby("Category")["Converted_CZK"].sum()

    for cat, amt in category_summary.items():
        st.markdown(f"**{cat}:** {amt:.2f} CZK")

    st.markdown(f"### 💰 Total Expenses: {total_sum:.2f} CZK")

    # --- Educational Tip ---
    top_category = category_summary.idxmax()
    percent = category_summary[top_category] / total_sum * 100
    if top_category == "Entertainment" and percent > 30:
        st.warning("💡 Watch out! You’re spending more than 30% on entertainment. Try saving a portion for unexpected expenses. 😉")
    else:
        st.info(f"Most of your spending went to _{top_category}_ ({percent:.1f}% of total expenses).")
else:
    st.info("No purchases yet. Add at least one to see your data ✨")
