import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "finance.db"
DB_PATH.parent.mkdir(exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # ============ SCHEMA ============
    c.executescript("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT DEFAULT 'cash',
        balance REAL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('income','expense')),
        budget REAL DEFAULT 0,
        UNIQUE(name, type)
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT CHECK(type IN ('income','expense')),
        amount REAL NOT NULL,
        category_id INTEGER,
        account_id INTEGER,
        note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(category_id) REFERENCES categories(id),
        FOREIGN KEY(account_id) REFERENCES accounts(id)
    );

    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        priority TEXT CHECK(priority IN ('low','medium','high')) DEFAULT 'medium',
        status TEXT CHECK(status IN ('considering','saving','bought','skipped'))
            DEFAULT 'considering',
        category TEXT,
        url TEXT,
        note TEXT,
        target_date TEXT,
        bought_date TEXT,
        actual_price REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ============ DEFAULT DATA (minimal) ============
    # App ကို စတင်သုံးနိုင်ဖို့ အနည်းဆုံး data ပဲ ထည့်
    # ကျန်တာ user ကိုယ်တိုင် Categories page ကနေ ထည့်နိုင်

    # Default accounts (၃ ခု)
    c.execute("SELECT COUNT(*) FROM accounts")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO accounts (name, type, balance) VALUES (?,?,?)",
            [
                ("Cash", "cash", 0),
                ("Bank", "bank", 0),
                ("Wallet", "wallet", 0),
            ],
        )

    
    conn.commit()
    conn.close()


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
    return last_id