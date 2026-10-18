import streamlit as st
import pandas as pd
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from core.db import query_df, DB_PATH
from core.utils import mmk, check_auth

st.set_page_config(page_title="Backup & Export", page_icon="📤", layout="wide")
check_auth()

st.title("📤 Backup & Export")
st.caption("Data တွေ export/backup လုပ်ပြီး သိမ်းထား")

# ============ SUMMARY ============
c1, c2, c3, c4, c5 = st.columns(5)

txn_count = query_df("SELECT COUNT(*) AS n FROM transactions")["n"][0]
acc_count = query_df("SELECT COUNT(*) AS n FROM accounts")["n"][0]
cat_count = query_df("SELECT COUNT(*) AS n FROM categories")["n"][0]
wish_count = query_df("SELECT COUNT(*) AS n FROM wishlist")["n"][0]
goal_count = query_df("SELECT COUNT(*) AS n FROM goals")["n"][0]

c1.metric("💸 Transactions", txn_count)
c2.metric("🏦 Accounts", acc_count)
c3.metric("🏷 Categories", cat_count)
c4.metric("🛍 Wishlist", wish_count)
c5.metric("🐷 Goals", goal_count)

st.divider()

# ============ EXPORT SECTION ============
st.subheader("📊 Export to CSV")

tab1, tab2, tab3 = st.tabs(["📅 Date Range", "📦 All Data", "📈 Summary Report"])

# ---- Tab 1: Date Range Export ----
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        from_date = st.date_input(
            "From", value=date.today().replace(day=1)
        )
    with c2:
        to_date = st.date_input("To", value=date.today())

    df = query_df(
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

    if df.empty:
        st.info("ဒီ range မှာ transaction မရှိဘူး")
    else:
        st.caption(f"📊 {len(df)} transactions • Total: {mmk(df['amount'].sum())}")
        st.dataframe(df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "⬇️ Download CSV",
                csv,
                f"transactions_{from_date}_{to_date}.csv",
                "text/csv",
                use_container_width=True,
            )
        with col2:
            excel_buf = BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Transactions", index=False)
            st.download_button(
                "⬇️ Download Excel",
                excel_buf.getvalue(),
                f"transactions_{from_date}_{to_date}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# ---- Tab 2: Export All Data ----
with tab2:
    st.caption("အားလုံး table တွေကို Excel multi-sheet အဖြစ် export")

    if st.button("📦 Generate All-in-One Excel", type="primary", use_container_width=True):
        with st.spinner("Generating..."):
            excel_buf = BytesIO()

            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                # Sheet 1: Summary
                summary_data = {
                    "Metric": [
                        "Total Transactions",
                        "Total Accounts",
                        "Total Categories",
                        "Total Wishlist Items",
                        "Total Goals",
                        "Export Date",
                    ],
                    "Value": [
                        txn_count,
                        acc_count,
                        cat_count,
                        wish_count,
                        goal_count,
                        date.today().isoformat(),
                    ],
                }
                pd.DataFrame(summary_data).to_excel(
                    writer, sheet_name="Summary", index=False
                )

                # Sheet 2: Transactions
                txn_df = query_df(
                    """
                    SELECT t.id, t.date, t.type, t.amount,
                           c.name AS category, a.name AS account, t.note
                    FROM transactions t
                    LEFT JOIN categories c ON c.id = t.category_id
                    LEFT JOIN accounts a ON a.id = t.account_id
                    ORDER BY t.date DESC
                    """
                )
                txn_df.to_excel(writer, sheet_name="Transactions", index=False)

                # Sheet 3: Accounts
                acc_df = query_df("SELECT * FROM accounts")
                acc_df.to_excel(writer, sheet_name="Accounts", index=False)

                # Sheet 4: Categories
                cat_df = query_df("SELECT * FROM categories")
                cat_df.to_excel(writer, sheet_name="Categories", index=False)

                # Sheet 5: Wishlist
                wish_df = query_df("SELECT * FROM wishlist")
                wish_df.to_excel(writer, sheet_name="Wishlist", index=False)

                # Sheet 6: Goals
                goal_df = query_df("SELECT * FROM goals")
                goal_df.to_excel(writer, sheet_name="Goals", index=False)

            st.success("✅ Excel ဖန်တီးပြီး")
            st.download_button(
                "⬇️ Download All-in-One Excel",
                excel_buf.getvalue(),
                f"finance_backup_{date.today().isoformat()}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# ---- Tab 3: Summary Report ----
with tab3:
    st.caption("ဒီလ အတွက် summary report")

    from core.utils import month_range
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

    cat_summary = query_df(
        """
        SELECT c.name AS category, c.type, SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON c.id = t.category_id
        WHERE t.date >= ? AND t.date < ?
        GROUP BY c.id
        ORDER BY total DESC
        """,
        (start, end),
    )

    if st.button("📈 Generate Monthly Report", type="primary", use_container_width=True):
        with st.spinner("Generating..."):
            excel_buf = BytesIO()

            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                # Summary
                summary = pd.DataFrame({
                    "Metric": ["Income", "Expense", "Net", "Period"],
                    "Value": [
                        f"{income:,.0f} MMK",
                        f"{expense:,.0f} MMK",
                        f"{income - expense:,.0f} MMK",
                        f"{start} to {end}",
                    ],
                })
                summary.to_excel(writer, sheet_name="Summary", index=False)

                # Category breakdown
                if not cat_summary.empty:
                    cat_summary.to_excel(
                        writer, sheet_name="Categories", index=False
                    )

            st.success("✅ Report ဖန်တီးပြီး")
            st.download_button(
                "⬇️ Download Report",
                excel_buf.getvalue(),
                f"report_{start}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

st.divider()

# ============ BACKUP DB ============
st.subheader("💾 Database Backup")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**📥 Download Backup**")
    st.caption("DB file ကို download လုပ်ပြီး သိမ်းထား")

    if DB_PATH.exists():
        db_bytes = DB_PATH.read_bytes()
        st.download_button(
            "⬇️ Download finance.db",
            db_bytes,
            f"finance_backup_{date.today().isoformat()}.db",
            "application/octet-stream",
            use_container_width=True,
        )
        size_kb = len(db_bytes) / 1024
        st.caption(f"📦 Size: {size_kb:.1f} KB")
    else:
        st.warning("DB file မရှိဘူး")

with c2:
    st.markdown("**📤 Restore from Backup**")
    st.caption("⚠️ ရှိပြီးသား data အားလုံး ပျက်မယ်")

    uploaded = st.file_uploader(
        "Backup file (.db)",
        type=["db"],
        key="restore_db",
    )

    if uploaded is not None:
        if st.button("⚠️ Restore (data ပျက်မယ်)", type="primary", use_container_width=True):
            with st.spinner("Restoring..."):
                # Backup current
                if DB_PATH.exists():
                    old_backup = DB_PATH.parent / f"finance_before_restore_{date.today().isoformat()}.db"
                    old_backup.write_bytes(DB_PATH.read_bytes())

                # Write new
                DB_PATH.write_bytes(uploaded.read())
                st.success("✅ Restore ပြီး — page refresh လုပ်ပါ")
                st.balloons()

st.divider()

# ============ WARNING ============
st.warning(
    "⚠️ **သတိ:** Backup/Export ကို ပုံမှန် (တစ်ပတ်တစ်ခါ) လုပ်ပါ။ "
    "Restore လုပ်ရင် ရှိပြီးသား data ပျက်မယ်။"
)

st.caption("💡 Export ဖိုင်တွေကို Google Drive / Dropbox မှာ သိမ်းထားပါ")