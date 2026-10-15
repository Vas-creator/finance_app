import streamlit as st
from datetime import date
from core.db import query_df, execute
from core.utils import mmk, month_range

st.set_page_config(page_title="Budget", page_icon="🎯", layout="wide")
st.title("🎯 Monthly Budget")
st.caption(f"📅 {date.today().strftime('%B %Y')} — ဒီလ အသုံးစရိတ်")

start, end = month_range()

# ============ QUERY ============
df = query_df(
    """
    SELECT c.id, c.name AS category, c.budget,
           COALESCE(SUM(t.amount),0) AS spent
    FROM categories c
    LEFT JOIN transactions t
        ON t.category_id = c.id
       AND t.type='expense'
       AND t.date >= ? AND t.date < ?
    WHERE c.type='expense'
    GROUP BY c.id
    ORDER BY c.name
    """,
    (start, end),
)

if df.empty:
    st.info("Expense category မရှိသေးဘူး")
    st.stop()

df["remaining"] = df["budget"] - df["spent"]
df["usage"] = df.apply(
    lambda r: (r["spent"] / r["budget"] * 100) if r["budget"] > 0 else 0,
    axis=1,
)

# ============ SUMMARY ============
total_budget = df["budget"].sum()
total_spent = df["spent"].sum()
total_remaining = total_budget - total_spent

c1, c2, c3 = st.columns(3)
c1.metric("💰 စုစုပေါင်း Budget", mmk(total_budget))
c2.metric("📤 သုံးပြီး", mmk(total_spent))
c3.metric(
    "💵 ကျန်",
    mmk(total_remaining),
    delta=f"{(total_spent/total_budget*100):.0f}% သုံးပြီး"
    if total_budget > 0
    else None,
)

st.divider()

# ============ OVER-BUDGET ALERT ============
over = df[df["spent"] > df["budget"]]
if not over.empty:
    st.error(
        f"⚠️ **{len(over)}** category budget ကျော်နေတယ်: "
        + ", ".join(over["category"].tolist())
    )

# ============ PROGRESS BARS ============
st.subheader("📊 Category အလိုက်")

for _, row in df.iterrows():
    usage = row["usage"]

    if usage < 80:
        icon, status = "🟢", "ကောင်း"
    elif usage < 100:
        icon, status = "🟡", "သတိ"
    else:
        icon, status = "🔴", "ကျော်နေတယ်"

    c1, c2, c3 = st.columns([4, 2, 1])

    with c1:
        st.markdown(f"**{icon} {row['category']}**")
        st.progress(
            min(usage / 100, 1.0),
            text=f"{mmk(row['spent'])} / {mmk(row['budget'])} ({usage:.0f}%)",
        )

    with c2:
        delta = row["remaining"]
        if delta >= 0:
            st.metric("ကျန်", mmk(delta))
        else:
            st.metric("ကျော်", mmk(abs(delta)), delta_color="inverse")

    with c3:
        if st.button("✏️", key=f"edit_budget_{row['id']}", use_container_width=True):
            st.session_state[f"editing_budget_{row['id']}"] = True

    # Edit form
    if st.session_state.get(f"editing_budget_{row['id']}"):
        with st.form(f"budget_form_{row['id']}"):
            st.markdown(f"**✏️ {row['category']} budget ပြင်**")
            new_budget = st.number_input(
                "Budget (ကျပ်)",
                min_value=0.0,
                value=float(row["budget"]),
                step=10000.0,
            )
            csave, ccancel = st.columns(2)
            if csave.form_submit_button("💾 Save", use_container_width=True):
                execute(
                    "UPDATE categories SET budget=? WHERE id=?",
                    (new_budget, row["id"]),
                )
                st.session_state[f"editing_budget_{row['id']}"] = False
                st.success("✅ ပြင်ပြီး")
                st.rerun()
            if ccancel.form_submit_button("Cancel", use_container_width=True):
                st.session_state[f"editing_budget_{row['id']}"] = False
                st.rerun()

    st.divider()

# ============ BULK EDIT ============
with st.expander("⚙️ Budget အားလုံး တစ်ခါတည်း ပြင်"):
    with st.form("bulk_budget_form"):
        st.caption("Category တစ်ခုချင်း budget သတ်မှတ်")
        new_budgets = {}
        for _, row in df.iterrows():
            new_budgets[row["id"]] = st.number_input(
                row["category"],
                min_value=0.0,
                value=float(row["budget"]),
                step=10000.0,
                key=f"bulk_{row['id']}",
            )

        if st.form_submit_button("💾 အားလုံး Save", use_container_width=True):
            for cat_id, budget in new_budgets.items():
                execute(
                    "UPDATE categories SET budget=? WHERE id=?",
                    (budget, cat_id),
                )
            st.success("✅ အားလုံး ပြင်ပြီး")
            st.rerun()