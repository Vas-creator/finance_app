import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from core.db import init_db, query_df
from core.utils import mmk, month_range

st.set_page_config(
    page_title="My Finance",
    page_icon="💰",
    layout="wide",
)

# ============ AUTH ============
with open("config.yaml", encoding="utf-8") as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

authenticator.login(location="main")

auth_status = st.session_state.get("authentication_status")

if auth_status is False:
    st.error("❌ Username သို့ Password မှားနေတယ်")
    st.stop()

if auth_status is None:
    st.warning("👋 ဝင်ရောက်ဖို့ Login လုပ်ပါ")
    st.stop()

# ============ SIDEBAR LOGOUT ============
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.get('name', 'User')}**")
    st.caption(st.session_state.get("username", ""))
    authenticator.logout("🚪 Logout", "sidebar")
    st.divider()

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

# ============ 2. CHARTS ROW ============
c_left, c_right = st.columns(2)

# Pie chart — expense by category
with c_left:
    st.subheader("🥧 Category အလိုက် သုံးငွေ")

    pie_df = query_df(
        """
        SELECT c.name AS category, SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON c.id = t.category_id
        WHERE t.type='expense' AND t.date>=? AND t.date<?
        GROUP BY c.id
        ORDER BY total DESC
        """,
        (start, end),
    )

    if pie_df.empty:
        st.info("ဒီလ သုံးငွေ မရှိသေးဘူး")
    else:
        fig = px.pie(
            pie_df,
            names="category",
            values="total",
            hole=0.45,
        )
        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

# Bar chart — 6-month trend
with c_right:
    st.subheader("📈 ၆ လ အတွင်း Trend")

    six_months_ago = (date.today().replace(day=1) - timedelta(days=180)).isoformat()

    trend_df = query_df(
        """
        SELECT strftime('%Y-%m', date) AS month,
               SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expense
        FROM transactions
        WHERE date >= ?
        GROUP BY month
        ORDER BY month
        """,
        (six_months_ago,),
    )

    if trend_df.empty:
        st.info("Data မရှိသေးဘူး")
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=trend_df["month"],
                y=trend_df["income"],
                name="📥 Income",
                marker_color="#10b981",
            )
        )
        fig.add_trace(
            go.Bar(
                x=trend_df["month"],
                y=trend_df["expense"],
                name="📤 Expense",
                marker_color="#ef4444",
            )
        )
        fig.update_layout(
            barmode="group",
            height=320,
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============ 3. ACCOUNTS + TOP CATEGORIES ============
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("🏦 Accounts")
    accounts = query_df("SELECT name, type, balance FROM accounts")
    if accounts.empty:
        st.info("Account မရှိသေးဘူး")
    else:
        for _, acc in accounts.iterrows():
            c1, c2 = st.columns([3, 2])
            icon = {"cash": "💵", "bank": "🏦", "wallet": "📱", "credit": "💳"}.get(
                acc["type"], "💼"
            )
            c1.markdown(f"**{icon} {acc['name']}**")
            c2.markdown(f"### {mmk(acc['balance'])}")
        st.caption(f"💰 **စုစုပေါင်း: {mmk(accounts['balance'].sum())}**")

with c_right:
    st.subheader("🔥 Top 5 သုံးငွေ")

    top_df = query_df(
        """
        SELECT c.name AS category, SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON c.id = t.category_id
        WHERE t.type='expense' AND t.date>=? AND t.date<?
        GROUP BY c.id
        ORDER BY total DESC
        LIMIT 5
        """,
        (start, end),
    )

    if top_df.empty:
        st.info("Data မရှိသေးဘူး")
    else:
        for i, (_, row) in enumerate(top_df.iterrows(), 1):
            c1, c2 = st.columns([4, 2])
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i - 1]
            c1.markdown(f"{medal} **{row['category']}**")
            c2.markdown(f"**{mmk(row['total'])}**")

st.divider()

# ============ 4. GOALS + WISHLIST ============
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("🐷 Goals")
    goals = query_df("SELECT name, target, saved FROM goals ORDER BY id DESC LIMIT 3")
    if goals.empty:
        st.info("Goal မရှိသေးဘူး")
    else:
        for _, g in goals.iterrows():
            pct = min(g["saved"] / g["target"], 1.0) if g["target"] > 0 else 0
            st.markdown(f"**{g['name']}** — {mmk(g['saved'])} / {mmk(g['target'])}")
            st.progress(pct)

with c_right:
    st.subheader("🛍 Wishlist")
    wish = query_df(
        """
        SELECT name, price, priority FROM wishlist
        WHERE status IN ('considering', 'saving')
        ORDER BY
            CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            id DESC
        LIMIT 3
        """
    )
    if wish.empty:
        st.info("ဝယ်ချင်တာ မရှိသေးဘူး")
    else:
        total = wish["price"].sum()
        st.caption(f"📦 {len(wish)} ခု • **{mmk(total)}**")
        for _, w in wish.iterrows():
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[w["priority"]]
            st.markdown(f"{icon} **{w['name']}** — {mmk(w['price'])}")

st.divider()

# ============ 5. RECENT TRANSACTIONS ============
st.subheader("📌 နောက်ဆုံး လုပ်ဆောင်ချက်")

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
    st.info("Transaction မရှိသေးဘူး — Transactions page မှာ ထည့်ပါ")
else:
    for _, r in recent.iterrows():
        icon = {"income": "📥", "expense": "📤"}[r["type"]]
        sign = {"income": "+", "expense": "-"}[r["type"]]
        color = {"income": "green", "expense": "red"}[r["type"]]

        c1, c2, c3 = st.columns([2, 4, 3])
        c1.markdown(f"{icon} `{r['date']}`")
        c2.markdown(f"**{r['category'] or r['type']}** · _{r['account'] or ''}_")
        c3.markdown(f":{color}[**{sign}{mmk(r['amount'])}**]")

st.divider()
st.caption("👈 ဘေးက sidebar ကနေ တခြား page တွေ ရွှေ့ကြည့်ပါ")