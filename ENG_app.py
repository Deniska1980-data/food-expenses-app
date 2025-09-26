import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="My Monthly Expense Diary", page_icon="🧾", layout="wide")

st.title("🧾 My Monthly Expense Diary")
st.write("Log your expenses, track conversions to CZK, and keep your budget under control.")

# --- Initialize dataframe in session state ---
if "purchases" not in st.session_state:
    st.session_state["purchases"] = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Amount (CZK)"])

# Form for entering a purchase
with st.form("purchase_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        purchase_date = st.date_input("Date", value=date.today())
        shop = st.text_input("Shop")
        country = st.selectbox("Country", ["Czechia", "Slovakia", "Croatia", "Other"])
        category = st.selectbox(
            "Category",
            ["Food", "Groceries", "Transport", "Restaurants & Bars", "Entertainment"]
        )
    with col2:
        amount = st.number_input("Amount", min_value=0.0, step=0.5, format="%.2f")
        currency = st.selectbox("Currency", ["CZK (Czech koruna)", "EUR (Euro)", "USD (US Dollar)", "GBP (British Pound)"])
        note = st.text_area("Note")
    
    submitted = st.form_submit_button("💾 Save purchase")

# Conversion rates to CZK (for demo, fixed values)
exchange_rates = {
    "CZK (Czech koruna)": 1.0,
    "EUR (Euro)": 25.0,
    "USD (US Dollar)": 23.0,
    "GBP (British Pound)": 29.0
}

# Save purchase
# Save purchase
if submitted:
    amount_czk = amount * exchange_rates[currency]
    st.session_state["purchases"].append({
        "date": st.date_input("📅 Date"),
        "shop": st.text_input("🏪 Shop"),
        "country": st.selectbox("🌍 Country", ["Czechia", "Slovakia", "Croatia", "Other"]),
        "currency": st.selectbox("💱 Currency", ["CZK (Czech koruna)", "EUR (Euro)", "USD (US Dollar)", "GBP (British Pound)"]),
        "amount": st.number_input("💰 Amount", min_value=0.0, step=0.5),
        "category": st.selectbox("📂 Category", ["Food", "Drugstore", "Transport", "Restaurants & Bars", "Entertainment"]),
        "note": st.text_input("📝 Note (e.g. shampoo, beer in bar...)")
    })
    st.success("✅ Purchase saved!")

# Show purchase list
# --- Initialize dataframe in session state ---
if "purchases" not in st.session_state:
    st.session_state["purchases"] = pd.DataFrame(columns=[
        "Date", "Shop", "Country", "Currency", "Amount", "Category", "Note", "Amount (CZK)"])

    # Monthly summary by category
    st.subheader("📊 Monthly Expense Summary")
    summary = df.groupby("Category")["Amount (CZK)"].sum().reset_index()
    st.dataframe(summary)

    total = df["Amount (CZK)"].sum()
    st.write(f"**Total Expenses:** {total:.2f} CZK")

    # Warning if entertainment > 30%
    if "Entertainment" in summary["Category"].values:
        entertainment = summary.loc[summary["Category"] == "Entertainment", "Amount (CZK)"].values[0]
        if entertainment / total > 0.3:
            st.warning("⚠️ Warning: You are spending more than 30% on Entertainment.")







