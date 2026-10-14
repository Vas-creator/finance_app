import streamlit as st
from datetime import date
from core.db import init_db, query_df
from core.utils import mmk, month_range

st.set_page_config(
    page_title="My Finance",
    page_icon="💰",
    layout="wide",
)

init_db()

# ============ HEADER ============
st.title("💰 My Personal Finance")
st.caption(f"📅 {date.today().strftime('%B %d, %Y')}")
st.divider()

# ============ 1. MONTHLY SUMMARY ============
start, end = month_range()

income = query_df(
    "SELECT COALESCE(SUM(amount),0) AS v FROM transactions "
    "WHERE type='income' AND date>=? AND date<?",
    (start, end),
)["v"][0]

expense = query_df(
    "SELECT COALESCE(SUM(amount),0) AS v FROM transactions "
    "WHERE type='expense' AND date>=? AND date<?",
    (start, end),
)["v"][0]

net = income - expense

st.subheader("📊 ဒီလ အကျဉ်းချုပ်")
c1, c2, c3 = st.columns(3)
c1.metric("📥 ဝင်ငွေ", mmk(income))
c2.metric("📤 ထွက်ငွေ", mmk(expense))
c3.metric("💵 ကျန်ငွေ", mmk(net))

st.divider()

# ============ 2. ACCOUNTS ============
st.subheader("🏦 Accounts")
accounts = query_df("SELECT name, type, balance FROM accounts")

if accounts.empty:
    st.info("Account မရှိသေးဘူး")
else:
    cols = st.columns(len(accounts))
    for col, (_, row) in zip(cols, accounts.iterrows()):
        col.metric(row["name"], mmk(row["balance"]))
    st.caption(f"💰 စုစုပေါင်း: **{mmk(accounts['balance'].sum())}**")

st.divider()

# ============ 3. RECENT TRANSACTIONS ============
st.subheader("📌 နောက်ဆုံး ၅ ခု")
recent = query_df(
    """
    SELECT t.date, t.type, t.amount, c.name AS category, a.name AS account
    FROM transactions t
    LEFT JOIN categories c ON c.id = t.category_id
    LEFT JOIN accounts a ON a.id = t.account_id
    ORDER BY t.date DESC, t.id DESC
    LIMIT 5
    """
)

if recent.empty:
    st.info("Transaction မရှိသေးဘူး — 👈 Transactions page မှာ ထည့်ပါ")
else:
    for _, r in recent.iterrows():
        icon = "📥" if r["type"] == "income" else "📤"
        sign = "+" if r["type"] == "income" else "-"
        color = "green" if r["type"] == "income" else "red"

        c1, c2, c3 = st.columns([2, 4, 3])
        c1.markdown(f"{icon} `{r['date']}`")
        c2.markdown(f"**{r['category'] or r['type']}** · _{r['account'] or ''}_")
        c3.markdown(f":{color}[**{sign}{mmk(r['amount'])}**]")

st.divider()
st.caption("👈 ဘေးက sidebar ကနေ Transactions page ရွှေ့ပါ")