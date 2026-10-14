from datetime import date
from dateutil.relativedelta import relativedelta    


def mmk(amount) -> str:
    """Myanmar Kyat format"""
    try:
        return f"{float(amount):,.0f} ကျပ်"
    except (ValueError, TypeError):
        return "0 ကျပ်"


def month_range(d: date = None):
    """Return (start, end) ISO strings for the month of d"""
    d = d or date.today()
    start = d.replace(day=1)
    end = start + relativedelta(months=1)
    return start.isoformat(), end.isoformat()


def recalc_account_balances():
    """Recalculate all account balances from transactions"""
    from core.db import query_df, get_conn

    accounts = query_df("SELECT id FROM accounts")
    conn = get_conn()
    c = conn.cursor()

    for acc_id in accounts["id"]:
        row = c.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN type='income' AND account_id=? THEN amount END),0)
              - COALESCE(SUM(CASE WHEN type='expense' AND account_id=? THEN amount END),0)
            FROM transactions
            """,
            (acc_id, acc_id),
        ).fetchone()[0]

        c.execute("UPDATE accounts SET balance=? WHERE id=?", (row, acc_id))

    conn.commit()
    conn.close()