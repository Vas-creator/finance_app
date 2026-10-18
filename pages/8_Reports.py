import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from core.db import query_df
from core.utils import mmk, check_auth

st.set_page_config(page_title="Reports", page_icon="📈", layout="wide")
check_auth()

st.title("📈 Reports & Analytics")
st.caption("ငွေရေးကြေးရေး ခွဲခြမ်းစိတ်ဖြာ")

# ============ DATE RANGE SELECTOR ============
st.subheader("📅 Date Range")

c1, c2, c3 = st.columns([2, 2, 3])

with c1:
    preset = st.selectbox(
        "Period",
        ["This Month", "Last Month", "Last 3 Months", "Last 6 Months",
         "This Year", "Last Year", "Custom"],
    )

today = date.today()

if preset == "This Month":
    from_date = today.replace(day=1)
    to_date = today
elif preset == "Last Month":
    first_this = today.replace(day=1)
    last_month_end = first_this - timedelta(days=1)
    from_date = last_month_end.replace(day=1)
    to_date = last_month_end
elif preset == "Last 3 Months":
    from_date = (today.replace(day=1) - timedelta(days=90))
    to_date = today
elif preset == "Last 6 Months":
    from_date = (today.replace(day=1) - timedelta(days=180))
    to_date = today
elif preset == "This Year":
    from_date = today.replace(month=1, day=1)
    to_date = today
elif preset == "Last Year":
    from_date = today.replace(year=today.year - 1, month=1, day=1)
    to_date = today.replace(year=today.year - 1, month=12, day=31)
else:
    with c2:
        from_date = st.date_input("From", value=today.replace(day=1))
    with c3:
        to_date = st.date_input("To", value=today)

st.caption(f"📅 {from_date.strftime('%b %d, %Y')} → {to_date.strftime('%b %d, %Y')}")

st.divider()

# ============ QUERY DATA ============
txn_df = query_df(
    """
    SELECT t.id, t.date, t.type, t.amount,
           c.name AS category, a.name AS account, t.note
    FROM transactions t
    LEFT JOIN categories c ON c.id = t.category_id
    LEFT JOIN accounts a ON a.id = t.account_id
    WHERE t.date >= ? AND t.date <= ?
    ORDER BY t.date DESC
    """,
    (from_date.isoformat(), to_date.isoformat()),
)

if txn_df.empty:
    st.info("📭 ဒီ range မှာ transaction မရှိဘူး")
    st.stop()

# ============ SUMMARY METRICS ============
income = txn_df[txn_df["type"] == "income"]["amount"].sum()
expense = txn_df[txn_df["type"] == "expense"]["amount"].sum()
net = income - expense
savings_rate = (net / income * 100) if income > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("📥 ဝင်ငွေ", mmk(income))
c2.metric("📤 ထွက်ငွေ", mmk(expense))
c3.metric("💵 ကျန်ငွေ", mmk(net))
c4.metric("💰 Savings Rate", f"{savings_rate:.1f}%")

st.divider()

# ============ CATEGORY BREAKDOWN ============
st.subheader("📊 Category Breakdown")

tab1, tab2 = st.tabs(["📤 Expense", "📥 Income"])

with tab1:
    exp_df = (
        txn_df[txn_df["type"] == "expense"]
        .groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    if exp_df.empty:
        st.info("ထွက်ငွေ မရှိဘူး")
    else:
        c1, c2 = st.columns([1, 1])

        with c1:
            fig = px.pie(
                exp_df,
                names="category",
                values="amount",
                hole=0.45,
                title="Expense by Category",
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = px.bar(
                exp_df.head(10),
                x="amount",
                y="category",
                orientation="h",
                title="Top 10 Expense Categories",
                color="amount",
                color_continuous_scale="Reds",
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Table
        with st.expander("📋 Category Detail"):
            exp_df["amount_formatted"] = exp_df["amount"].apply(mmk)
            exp_df["%"] = (exp_df["amount"] / exp_df["amount"].sum() * 100).round(1)
            st.dataframe(
                exp_df[["category", "amount_formatted", "%"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "category": "Category",
                    "amount_formatted": "Amount",
                    "%": "%",
                },
            )

with tab2:
    inc_df = (
        txn_df[txn_df["type"] == "income"]
        .groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )

    if inc_df.empty:
        st.info("ဝင်ငွေ မရှိဘူး")
    else:
        c1, c2 = st.columns([1, 1])

        with c1:
            fig = px.pie(
                inc_df,
                names="category",
                values="amount",
                hole=0.45,
                title="Income by Category",
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = px.bar(
                inc_df,
                x="amount",
                y="category",
                orientation="h",
                title="Income Sources",
                color="amount",
                color_continuous_scale="Greens",
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============ TREND ANALYSIS ============
st.subheader("📈 Trend Analysis")

trend_df = query_df(
    """
    SELECT strftime('%Y-%m', date) AS month,
           SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS income,
           SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expense
    FROM transactions
    WHERE date >= ? AND date <= ?
    GROUP BY month
    ORDER BY month
    """,
    (from_date.isoformat(), to_date.isoformat()),
)

if trend_df.empty:
    st.info("Trend data မရှိဘူး")
else:
    trend_df["net"] = trend_df["income"] - trend_df["expense"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend_df["month"],
            y=trend_df["income"],
            name="📥 Income",
            mode="lines+markers",
            line=dict(color="#10b981", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend_df["month"],
            y=trend_df["expense"],
            name="📤 Expense",
            mode="lines+markers",
            line=dict(color="#ef4444", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend_df["month"],
            y=trend_df["net"],
            name="💵 Net",
            mode="lines+markers",
            line=dict(color="#3b82f6", width=2, dash="dash"),
        )
    )
    fig.update_layout(
        height=400,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Stacked bar
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=trend_df["month"],
            y=trend_df["income"],
            name="Income",
            marker_color="#10b981",
        )
    )
    fig2.add_trace(
        go.Bar(
            x=trend_df["month"],
            y=trend_df["expense"],
            name="Expense",
            marker_color="#ef4444",
        )
    )
    fig2.update_layout(
        barmode="group",
        height=350,
        title="Monthly Comparison",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ============ ACCOUNT BREAKDOWN ============
st.subheader("🏦 Account Breakdown")

acc_df = query_df(
    """
    SELECT a.name AS account, t.type,
           SUM(t.amount) AS total
    FROM transactions t
    JOIN accounts a ON a.id = t.account_id
    WHERE t.date >= ? AND t.date <= ?
    GROUP BY a.id, t.type
    """,
    (from_date.isoformat(), to_date.isoformat()),
)

if acc_df.empty:
    st.info("Account data မရှိဘူး")
else:
    pivot = acc_df.pivot_table(
        index="account", columns="type", values="total", fill_value=0
    ).reset_index()

    if "income" not in pivot.columns:
        pivot["income"] = 0
    if "expense" not in pivot.columns:
        pivot["expense"] = 0

    pivot["net"] = pivot["income"] - pivot["expense"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(name="📥 Income", x=pivot["account"], y=pivot["income"], marker_color="#10b981")
    )
    fig.add_trace(
        go.Bar(name="📤 Expense", x=pivot["account"], y=pivot["expense"], marker_color="#ef4444")
    )
    fig.add_trace(
        go.Bar(name="💵 Net", x=pivot["account"], y=pivot["net"], marker_color="#3b82f6")
    )
    fig.update_layout(
        barmode="group",
        height=400,
        title="Account-wise Breakdown",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ============ EXPORT ============
st.subheader("📤 Export Report")

from io import BytesIO

if st.button("📊 Generate Excel Report", type="primary", use_container_width=True):
    with st.spinner("Generating..."):
        buf = BytesIO()

        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            # Summary
            summary = pd.DataFrame({
                "Metric": [
                    "Period", "Income", "Expense", "Net",
                    "Savings Rate", "Transactions",
                ],
                "Value": [
                    f"{from_date} to {to_date}",
                    mmk(income),
                    mmk(expense),
                    mmk(net),
                    f"{savings_rate:.1f}%",
                    len(txn_df),
                ],
            })
            summary.to_excel(writer, sheet_name="Summary", index=False)

            # Transactions
            txn_export = txn_df.copy()
            txn_export.to_excel(writer, sheet_name="Transactions", index=False)

            # Expense by Category
            if not exp_df.empty:
                exp_df.to_excel(writer, sheet_name="Expense Categories", index=False)

            # Income by Category
            if not inc_df.empty:
                inc_df.to_excel(writer, sheet_name="Income Categories", index=False)

            # Trend
            if not trend_df.empty:
                trend_df.to_excel(writer, sheet_name="Monthly Trend", index=False)

        st.success("✅ Report ဖန်တီးပြီး")
        st.download_button(
            "⬇️ Download Report",
            buf.getvalue(),
            f"report_{from_date}_{to_date}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

st.caption("💡 Reports ကို လစဉ် review လုပ်ပါ")