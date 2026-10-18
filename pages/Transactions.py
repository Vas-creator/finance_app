import streamlit as st
import pandas as pd 
from datetime import date
from core.db import query_df, execute
from core.utils import mmk, recalc_account_balances, check_auth

st.set_page_config(page_title="Transactions", page_icon="💸", layout="wide")
check_auth()   # ← ဒါကို ထည့်

st.title("💸 Transactions")

accounts = query_df("SELECT id, name FROM accounts")
categories = query_df("SELECT id, name, type FROM categories")

tab1, tab2 = st.tabs(["➕ Add", "📋 List"])

# ============ ADD ============
# ============ ADD ============
with tab1:
    # Type selector (form အပြင် — auto update အတွက်)
    txn_type = st.radio(
        "Type",
        ["expense", "income"],
        horizontal=True,
        key="txn_type_radio",
        format_func=lambda x: "📤 expense" if x == "expense" else "📥 income",
    )

    # Category quick-add (form အပြင်)
    with st.expander("➕ Category အသစ် ထည့်", expanded=False):
        with st.form("quick_cat", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            new_cat_name = c1.text_input("Name *", placeholder="Transport")
            new_cat_type = c2.selectbox(
                "Type",
                ["expense", "income"],
                index=0 if txn_type == "expense" else 1,
            )
            new_cat_budget = c3.number_input(
                "Budget (ကျပ်)", min_value=0.0, step=10000.0
            )

            if st.form_submit_button("💾 Category Add", use_container_width=True):
                if not new_cat_name.strip():
                    st.error("Name ဖြည့်ပါ")
                else:
                    dup = query_df(
                        "SELECT id FROM categories WHERE name=? AND type=?",
                        (new_cat_name.strip(), new_cat_type),
                    )
                    if not dup.empty:
                        st.warning(f"'{new_cat_name}' ({new_cat_type}) ရှိပြီးသား")
                    else:
                        execute(
                            "INSERT INTO categories (name, type, budget) VALUES (?,?,?)",
                            (
                                new_cat_name.strip(),
                                new_cat_type,
                                new_cat_budget if new_cat_type == "expense" else 0,
                            ),
                        )
                        st.success(f"✅ '{new_cat_name}' ထည့်ပြီး")
                        st.rerun()

    # Transaction form
    with st.form("txn_form", clear_on_submit=True):
        # Categories ကို ပြန် query (အသစ် ထည့်ပြီးရင် refresh)
        categories = query_df("SELECT id, name, type FROM categories")
        cat_filtered = categories[categories["type"] == txn_type]

        c1, c2 = st.columns(2)

        with c1:
            amount = st.number_input(
                "Amount (ကျပ်)", min_value=0.0, step=1000.0
            )
            txn_date = st.date_input("Date", value=date.today())

        with c2:
            account = st.selectbox("Account", accounts["name"])

            if cat_filtered.empty:
                st.warning(f"⚠️ {txn_type} category မရှိသေးဘူး — အပေါ်မှာ ထည့်ပါ")
                category = None
            else:
                category = st.selectbox("Category", cat_filtered["name"])

            note = st.text_input("Note")

        submitted = st.form_submit_button("💾 Save", use_container_width=True)

        if submitted:
            if amount <= 0:
                st.error("Amount က 0 ထက် ကြီးရမယ်")
            elif not category:
                st.error("Category မရှိသေးဘူး — အပေါ်မှာ ထည့်ပါ")
            else:
                acc_id = int(
                    accounts.loc[accounts["name"] == account, "id"].iloc[0]
                )
                cat_id = int(
                    cat_filtered.loc[cat_filtered["name"] == category, "id"].iloc[0]
                )

                execute(
                    """
                    INSERT INTO transactions
                        (date, type, amount, category_id, account_id, note)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        txn_date.isoformat(),
                        txn_type,
                        amount,
                        cat_id,
                        acc_id,
                        note,
                    ),
                )

                recalc_account_balances()
                st.success("✅ သိမ်းပြီးပါပြီ")
                st.rerun()
# ============ LIST ============
with tab2:
    df = query_df(
        """
        SELECT t.id, t.date, t.type, t.amount,
               c.name AS category, a.name AS account, t.note
        FROM transactions t
        LEFT JOIN categories c ON c.id = t.category_id
        LEFT JOIN accounts a ON a.id = t.account_id
        ORDER BY t.date DESC, t.id DESC
        LIMIT 500
        """
    )

    if df.empty:
        st.info("Transaction မရှိသေးဘူး")
    else:
        # Filters
        c1, c2 = st.columns(2)
        with c1:
            ftype = st.multiselect(
                "Type",
                ["income", "expense"],
                default=["income", "expense"],
            )
        with c2:
            fdate = st.date_input(
                "From date", value=date.today().replace(day=1)
            )

        df = df[df["type"].isin(ftype)]
        df = df[pd.to_datetime(df["date"]).dt.date >= fdate]

        if df.empty:
            st.warning("Filter နဲ့ ကိုက်တာ မရှိဘူး")
        else:
            # Display with formatted amount
            display_df = df.copy()
            display_df["amount"] = display_df["amount"].apply(mmk)
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Summary
            total = df["amount"].sum()
            st.caption(f"📊 {len(df)} ခု • စုစုပေါင်း **{mmk(total)}**")

            # CSV Export
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Export CSV",
                csv,
                "transactions.csv",
                "text/csv",
            )

        # Delete
        st.divider()
        with st.expander("🗑 Transaction ဖျက်"):
            del_id = st.number_input(
                "Transaction ID", min_value=1, step=1, value=1
            )
            if st.button("🗑 Delete", type="secondary"):
                execute("DELETE FROM transactions WHERE id=?", (del_id,))
                recalc_account_balances()
                st.success(f"🗑 ID {del_id} ဖျက်ပြီး")
                st.rerun()