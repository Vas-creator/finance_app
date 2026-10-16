import streamlit as st
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
    # ၁. Type ကို form အပြင်မှာ ရွေး (auto update အတွက်)
    txn_type = st.radio(
        "Type",
        ["expense", "income"],
        horizontal=True,
        key="txn_type_radio",
    )

    # ၂. Filtered categories ကို type ပေါ်မူတည်ပြီး ချက်
    categories = query_df("SELECT id, name, type FROM categories")
    cat_filtered = categories[categories["type"] == txn_type]

    # ၃. Form ဖွင့်
    with st.form("txn_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "Amount (ကျပ်)", min_value=0.0, step=1000.0
            )
            txn_date = st.date_input("Date", value=date.today())

        with col2:
            account = st.selectbox("Account", accounts["name"])
            category = st.selectbox("Category", cat_filtered["name"])
            note = st.text_input("Note")

        submitted = st.form_submit_button("💾 Save", use_container_width=True)

        if submitted:
            if amount <= 0:
                st.error("Amount က 0 ထက် ကြီးရမယ်")
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