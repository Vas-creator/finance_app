import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "accounting.db"
DB_PATH.parent.mkdir(exist_ok=True)

def get_conn():
    """Database connection ရယူခြင်း"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_connection():
    """Alias for get_conn()"""
    return get_conn()

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        business_name TEXT,
        address TEXT,
        business_type TEXT,
        template_type TEXT DEFAULT 'manufacturing',
        fiscal_year_end TEXT DEFAULT '09-30',
        email TEXT,
        phone TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS statements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        fiscal_year TEXT NOT NULL,
        period_end TEXT NOT NULL,
        statement_type TEXT NOT NULL,
        status TEXT DEFAULT 'draft',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(client_id) REFERENCES clients(id),
        UNIQUE(client_id, fiscal_year, statement_type)
    );

    CREATE TABLE IF NOT EXISTS line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        statement_id INTEGER NOT NULL,
        sr_no TEXT,
        section TEXT,
        label TEXT NOT NULL,
        value REAL DEFAULT 0,
        indent_level INTEGER DEFAULT 0,
        is_calculated INTEGER DEFAULT 0,
        calc_type TEXT,
        calc_formula TEXT,
        is_bold INTEGER DEFAULT 0,
        sort_order INTEGER,
        FOREIGN KEY(statement_id) REFERENCES statements(id)
    );
    """)

    conn.commit()
    conn.close()


@st.cache_data(ttl=30)
def query_df(sql, params=()):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def execute(sql, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    st.cache_data.clear()
    return last_id

# core/db.py ထဲ ထည့်ရန်

def get_dashboard_stats() -> dict:
    """Dashboard အတွက် stats ရယူခြင်း"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Total clients
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        
        # Total statements
        try:
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM manufacturing) +
                    (SELECT COUNT(*) FROM trading_pl) +
                    (SELECT COUNT(*) FROM balance_sheet)
            """)
            total_statements = cursor.fetchone()[0]
        except Exception:
            total_statements = 0
        
        # Latest update
        try:
            cursor.execute("""
                SELECT MAX(updated_at) FROM clients
            """)
            latest = cursor.fetchone()[0]
            latest_update = latest[:10] if latest else "—"
        except Exception:
            latest_update = "—"
        
        return {
            "total_clients": total_clients,
            "total_statements": total_statements,
            "latest_update": latest_update,
        }
    finally:
        conn.close()


def get_recent_clients(limit: int = 5) -> list:
    """မကြာသေးမီ ဖောက်သည်များ ရယူခြင်း"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, business_type, phone, updated_at
            FROM clients
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

# ============================================================
# CLIENT CRUD
# ============================================================

def create_client(name: str, business_name: str = "",
                  business_type: str = "", email: str = "",
                  address: str = "", fiscal_year_end: str = "09-30",
                  **kwargs) -> int:
    """ဖောက်သည် အသစ် ဖန်တီးခြင်း"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO clients 
                (name, business_name, business_type, email, address, fiscal_year_end)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, business_name, business_type, email, address, fiscal_year_end))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_clients() -> list:
    """ဖောက်သည် အားလုံး"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, business_name, business_type, email, 
                   address, fiscal_year_end, created_at, updated_at
            FROM clients
            ORDER BY name
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_client(client_id: int):
    """ဖောက်သည် တစ်ဦး"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, business_name, business_type, email,
                   address, fiscal_year_end, created_at, updated_at
            FROM clients
            WHERE id = ?
        """, (client_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_client(client_id: int, **kwargs) -> bool:
    """ဖောက်သည် ပြင်ဆင်ခြင်း"""
    if not kwargs:
        return False
    
    # Allow only these fields
    allowed = {"name", "business_name", "business_type", 
               "email", "address", "fiscal_year_end"}
    fields_to_update = {k: v for k, v in kwargs.items() if k in allowed}
    
    if not fields_to_update:
        return False
    
    set_clause = ", ".join(f"{k} = ?" for k in fields_to_update.keys())
    values = list(fields_to_update.values()) + [client_id]
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"UPDATE clients SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_client(client_id: int) -> bool:
    """ဖောက်သည် ဖျက်ခြင်း"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def count_clients() -> int:
    """ဖောက်သည် အရေအတွက်"""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM clients")
        return cursor.fetchone()[0]
    finally:
        conn.close()

def get_statement(client_id: int, statement_type: str):
    table_map = {
        "manufacturing": "manufacturing",
        "trading_pl": "trading_pl",
        "balance_sheet": "balance_sheet",
        "cash_flow": "cash_flow",           # ← ⚠️ ဒါ ပါမပါ စစ်ပါ
    }
    # ...
    
    table = table_map.get(statement_type)
    if not table:
        return None
    
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"SELECT * FROM {table} WHERE client_id = ? ORDER BY id DESC LIMIT 1",
            (client_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except Exception:
        return None
    finally:
        conn.close()


def save_statement(client_id: int, statement_type: str,
                   period_end: str = "", data_json: str = "",
                   as_at_date: str = "", **kwargs) -> int:
    """Save/update statement"""
    # save_statement() ထဲမှာ
    table_map = {
    "manufacturing": "manufacturing",
    "trading_pl": "trading_pl",
    "balance_sheet": "balance_sheet",
    "cash_flow": "cash_flow",           # ← အသစ်
    }

    # get_statement() ထဲမှာ
    table_map = {
    "manufacturing": "manufacturing",
    "trading_pl": "trading_pl",
    "balance_sheet": "balance_sheet",
    "cash_flow": "cash_flow",           # ← အသစ်
    }

    table = table_map.get(statement_type)
    if not table:
        raise ValueError(f"မသိသော statement type: {statement_type}")

    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Check if exists
        cursor.execute(f"SELECT id FROM {table} WHERE client_id = ? LIMIT 1", (client_id,))
        row = cursor.fetchone()

        # Balance Sheet အတွက် — as_at_date
        if statement_type == "balance_sheet":
            date_col = "as_at_date"
            date_val = as_at_date or period_end
        else:
            date_col = "period_end"
            date_val = period_end

        if row:
            cursor.execute(
                f"""UPDATE {table} 
                    SET {date_col} = ?, data = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?""",
                (date_val, data_json, row[0])
            )
            result_id = row[0]
        else:
            cursor.execute(
                f"""INSERT INTO {table} (client_id, {date_col}, data)
                    VALUES (?, ?, ?)""",
                (client_id, date_val, data_json)
            )
            result_id = cursor.lastrowid

        conn.commit()
        return result_id
    finally:
        conn.close()