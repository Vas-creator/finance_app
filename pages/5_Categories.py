import streamlit as st
from core.db import query_df, execute
from core.utils import mmk

st.set_page_config(page_title="Categories", page_icon="🏷", layout="wide")
st.title("🏷 Categories")
st.caption("ဝင်ငွေ/ထွက်ငွေ အမျိုးအစားတွေ စီမံ")

# ============ SUMMARY ============
all_cats = query_df("SELECT * FROM categories")
n_income = len(all_cats[all_cats["type"] == "income"])
n_expense = len(all_cats[all_cats["type"] == "expense"])

c1, c2, c3 = st.columns(3)
c1.metric("📦 စုစုပေါင်း", len(all_cats))
c2.metric("📥 Income", n_income)
c3.metric("📤 Expense", n_expense)

st.divider()

# ============ ADD CATEGORY ============
with st.expander("➕ Category အသစ် ထည့်", expanded=False):
    with st.form("add_cat_form", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Name *", placeholder="Food")
            cat_type = st.selectbox(
                "Type",
                ["expense", "income"],
                format_func=lambda x: "📤 Expense" if x == "expense" else "📥 Income",
            )

        with c2:
            budget = st.number_input(
                "Budget (ကျပ်)",
                min_value=0.0,
                step=10000.0,
                help="Expense category အတွက်ပဲ အသုံးဝင်",
            )
            st.caption(
                "💡 Budget က လစဉ် expense ကန့်သတ်ချက်"
                if cat_type == "expense"
                else "💡 Income အတွက် budget မလိုဘူး"
            )

        submitted = st.form_submit_button("💾 Save", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Name ဖြည့်ပါ")
            else:
                existing = query_df(
                    "SELECT id FROM categories WHERE name=? AND type=?",
                    (name.strip(), cat_type),
                )
                if not existing.empty:
                    st.error(f"'{name}' ({cat_type}) ရှိပြီးသား")
                else:
                    execute(
                        "INSERT INTO categories (name, type, budget) VALUES (?,?,?)",
                        (
                            name.strip(),
                            cat_type,
                            budget if cat_type == "expense" else 0,
                        ),
                    )
                    st.success(f"✅ '{name}' ထည့်ပြီး")
                    st.rerun()

st.divider()

# ============ FILTER ============
if all_cats.empty:
    st.info("Category မရှိသေးဘူး — ➕ နှိပ်ပြီး ထည့်ပါ")
    st.stop()

c1, c2 = st.columns(2)
with c1:
    type_filter = st.multiselect(
        "Type",
        ["income", "expense"],
        default=["income", "expense"],
        format_func=lambda x: "📥 Income" if x == "income" else "📤 Expense",
    )
with c2:
    sort_by = st.selectbox("စီရန်", ["Name (A-Z)", "Budget ကြီး→ငယ်", "အသစ်ဆုံး"])

df = all_cats[all_cats["type"].isin(type_filter)]

if sort_by == "Name (A-Z)":
    df = df.sort_values("name")
elif sort_by == "Budget ကြီး→ငယ်":
    df = df.sort_values("budget", ascending=False)
else:
    df = df.sort_values("id", ascending=False)

# ============ LIST ============
st.subheader(f"📋 Category စာရင်း ({len(df)})")

if df.empty:
    st.warning("Filter နဲ့ ကိုက်တာ မရှိဘူး")
    st.stop()

for _, cat in df.iterrows():
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

        with c1:
            icon = "📥" if cat["type"] == "income" else "📤"
            st.markdown(f"### {icon} {cat['name']}")
            st.caption(f"`{cat['type']}`")

        with c2:
            if cat["type"] == "expense":
                st.metric("Budget", mmk(cat["budget"]))
            else:
                st.metric("Budget", "—")

        with c3:
            # Transaction count
            txn_count = query_df(
                "SELECT COUNT(*) AS n FROM transactions WHERE category_id=?",
                (cat["id"],),
            )["n"][0]
            st.metric("Transactions", txn_count)

        with c4:
            c4a, c4b = st.columns(2)
            if c4a.button(
                "✏️", key=f"edit_cat_{cat['id']}", use_container_width=True
            ):
                st.session_state[f"editing_cat_{cat['id']}"] = True

            if c4b.button(
                "🗑", key=f"del_cat_{cat['id']}", use_container_width=True
            ):
                st.session_state[f"deleting_cat_{cat['id']}"] = True

        # ---------- Edit mode ----------
        if st.session_state.get(f"editing_cat_{cat['id']}"):
            with st.form(f"edit_cat_form_{cat['id']}"):
                st.markdown("**✏️ Category ပြင်**")
                ec1, ec2 = st.columns(2)

                with ec1:
                    new_name = st.text_input("Name", value=cat["name"])
                    new_type = st.selectbox(
                        "Type",
                        ["expense", "income"],
                        index=["expense", "income"].index(cat["type"]),
                        format_func=lambda x: "📤 Expense"
                        if x == "expense"
                        else "📥 Income",
                    )

                with ec2:
                    new_budget = st.number_input(
                        "Budget (ကျပ်)",
                        min_value=0.0,
                        value=float(cat["budget"]),
                        step=10000.0,
                    )

                csave, ccancel = st.columns(2)
                if csave.form_submit_button("💾 Save", use_container_width=True):
                    # Duplicate check (name + type ကွဲရင်)
                    dup = query_df(
                        "SELECT id FROM categories WHERE name=? AND type=? AND id!=?",
                        (new_name.strip(), new_type, cat["id"]),
                    )
                    if not dup.empty:
                        st.error(f"'{new_name}' ({new_type}) ရှိပြီးသား")
                    else:
                        execute(
                            "UPDATE categories SET name=?, type=?, budget=? WHERE id=?",
                            (
                                new_name.strip(),
                                new_type,
                                new_budget if new_type == "expense" else 0,
                                cat["id"],
                            ),
                        )
                        st.session_state[f"editing_cat_{cat['id']}"] = False
                        st.success("✅ ပြင်ပြီး")
                        st.rerun()

                if ccancel.form_submit_button("Cancel", use_container_width=True):
                    st.session_state[f"editing_cat_{cat['id']}"] = False
                    st.rerun()

        # ---------- Delete mode ----------
        if st.session_state.get(f"deleting_cat_{cat['id']}"):
            with st.form(f"del_cat_form_{cat['id']}"):
                st.warning(f"⚠️ **'{cat['name']}'** ကို ဖျက်မှာ သေချာလား?")

                txn_count = query_df(
                    "SELECT COUNT(*) AS n FROM transactions WHERE category_id=?",
                    (cat["id"],),
                )["n"][0]

                if txn_count > 0:
                    st.error(
                        f"⚠️ ဒီ category မှာ transaction **{txn_count} ခု** ရှိတယ်။"
                    )
                    delete_txns = st.checkbox(
                        f"Transaction {txn_count} ခုပါ ဖျက်မယ်",
                        key=f"del_txn_{cat['id']}",
                    )
                else:
                    delete_txns = True

                c_yes, c_no = st.columns(2)

                if c_yes.form_submit_button(
                    "🗑 ဖျက်", use_container_width=True, type="primary"
                ):
                    if txn_count > 0 and not delete_txns:
                        st.error("Transaction ဖျက်ဖို့ checkbox ကို အမှတ်ခြစ်ပါ")
                    else:
                        if delete_txns and txn_count > 0:
                            execute(
                                "DELETE FROM transactions WHERE category_id=?",
                                (cat["id"],),
                            )
                        execute("DELETE FROM categories WHERE id=?", (cat["id"],))
                        # Account balance recalc
                        from core.utils import recalc_account_balances

                        recalc_account_balances()
                        st.session_state[f"deleting_cat_{cat['id']}"] = False
                        st.success("🗑 ဖျက်ပြီး")
                        st.rerun()

                if c_no.form_submit_button("Cancel", use_container_width=True):
                    st.session_state[f"deleting_cat_{cat['id']}"] = False
                    st.rerun()

st.divider()
st.caption("💡 Category ဖျက်ရင် transaction တွေကို ရွေးပြီး ဖျက်နိုင်တယ်")