# core/utils.py
"""
Accounting App - Utility Functions
အဖေအတွက် အထောက်အကူပြု function များ

Author: [Your Name]
For: Retired Account Officer (Dad)
"""

import re
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Union, List, Dict, Any
import streamlit as st


# ============================================================
# 1. NUMBER FORMATTING
# ============================================================

def format_number(value: Union[int, float, Decimal, None], 
                  decimals: int = 2, 
                  use_commas: bool = True) -> str:
    """
    Number ကို comma-separated string အဖြစ် format လုပ်ခြင်း
    
    Examples:
        format_number(1234567.5)     -> '1,234,567.50'
        format_number(1234567.5, 0)  -> '1,234,568'
        format_number(None)          -> '0.00'
    """
    if value is None or value == "":
        value = 0
    
    try:
        num = Decimal(str(value))
    except (ValueError, TypeError):
        return "0.00"
    
    # Round
    quantize_str = "1." + ("0" * decimals) if decimals > 0 else "1"
    num = num.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
    
    # Format with commas
    if use_commas:
        if decimals > 0:
            return f"{num:,.{decimals}f}"
        else:
            return f"{num:,.0f}"
    else:
        if decimals > 0:
            return f"{num:.{decimals}f}"
        else:
            return f"{num:.0f}"


def format_currency(value: Union[int, float, Decimal, None], 
                    decimals: int = 2,
                    show_unit: bool = False) -> str:
    """
    ကျပ်ငွေ format လုပ်ခြင်း
    
    Examples:
        format_currency(1234567.5)              -> '1,234,567.50'
        format_currency(1234567.5, show_unit=True) -> '1,234,567.50 ကျပ်'
    """
    formatted = format_number(value, decimals)
    if show_unit:
        return f"{formatted} ကျပ်"
    return formatted


def format_myanmar_currency(value: Union[int, float, Decimal, None]) -> str:
    """
    မြန်မာ့ပုံစံ ငွေကြေး format (သိန်း/သန်း ဖြင့်)
    
    Examples:
        format_myanmar_currency(150000)    -> '1.50 သိန်း'
        format_myanmar_currency(25000000)  -> '2.50 သန်း'
        format_myanmar_currency(5000)      -> '5,000.00 ကျပ်'
    """
    if value is None:
        value = 0
    
    try:
        num = float(value)
    except (ValueError, TypeError):
        return "0.00 ကျပ်"
    
    abs_num = abs(num)
    
    if abs_num >= 10_000_000:  # 1 သန်း
        return f"{num / 1_000_000:,.2f} သန်း"
    elif abs_num >= 100_000:   # 1 သိန်း
        return f"{num / 100_000:,.2f} သိန်း"
    else:
        return f"{format_number(num)} ကျပ်"


def parse_number(value: Any) -> float:
    """
    String/input ကို float အဖြစ် ပြောင်းခြင်း (commas ဖယ်ရှား)
    
    Examples:
        parse_number('1,234,567.50') -> 1234567.5
        parse_number('')             -> 0.0
        parse_number(None)           -> 0.0
    """
    if value is None or value == "":
        return 0.0
    
    if isinstance(value, (int, float, Decimal)):
        return float(value)
    
    # Remove commas and spaces
    cleaned = str(value).replace(",", "").replace(" ", "").strip()
    
    if cleaned == "" or cleaned == "-":
        return 0.0
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


# ============================================================
# 2. DATE HELPERS
# ============================================================

MYANMAR_MONTHS = {
    1: "ဇန်နဝါရီ", 2: "ဖေဖော်ဝါရီ", 3: "မတ်", 4: "ဧပြီ",
    5: "မေ", 6: "ဇွန်", 7: "ဇူလိုင်", 8: "ဩဂုတ်",
    9: "စက်တင်ဘာ", 10: "အောက်တိုဘာ", 11: "နိုဝင်ဘာ", 12: "ဒီဇင်ဘာ"
}

def format_date_mm(d: Union[date, datetime, str, None]) -> str:
    """
    ရက်စွဲကို မြန်မာ့ပုံစံ format လုပ်ခြင်း
    
    Examples:
        format_date_mm(date(2024, 3, 15)) -> '၁၅ မတ် ၂၀၂၄'
    """
    if d is None:
        return ""
    
    if isinstance(d, str):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return d
    
    if isinstance(d, datetime):
        d = d.date()
    
    month_mm = MYANMAR_MONTHS.get(d.month, "")
    return f"{d.day} {month_mm} {d.year}"


def format_date_en(d: Union[date, datetime, str, None]) -> str:
    """ISO format (YYYY-MM-DD)"""
    if d is None:
        return ""
    if isinstance(d, str):
        return d
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime("%Y-%m-%d")


def today_str() -> str:
    """ယနေ့ရက်စွဲ ISO string"""
    return date.today().strftime("%Y-%m-%d")


def get_fiscal_year_range(fy_end: date = None) -> tuple:
    """
    ဘဏ္ဍာရေးနှစ် ကာလ ရယူခြင်း
    Default: ဧပြီ ၁ မှ မတ် ၃၁ အထိ (မြန်မာ့ဘဏ္ဍာရေးနှစ်)
    """
    if fy_end is None:
        fy_end = date.today()
    
    if fy_end.month >= 4:
        start = date(fy_end.year, 4, 1)
        end = date(fy_end.year + 1, 3, 31)
    else:
        start = date(fy_end.year - 1, 4, 1)
        end = date(fy_end.year, 3, 31)
    
    return start, end


# ============================================================
# 3. ACCOUNTING CALCULATIONS
# ============================================================

def calc_prime_cost(direct_materials: float, 
                    direct_labour: float, 
                    direct_expenses: float = 0) -> float:
    """
    Prime Cost = Direct Materials + Direct Labour + Direct Expenses
    """
    return parse_number(direct_materials) + \
           parse_number(direct_labour) + \
           parse_number(direct_expenses)


def calc_production_cost(prime_cost: float, 
                         factory_overhead: float,
                         opening_wip: float = 0,
                         closing_wip: float = 0) -> float:
    """
    Production Cost = Prime Cost + Factory Overhead + Opening WIP - Closing WIP
    """
    return parse_number(prime_cost) + \
           parse_number(factory_overhead) + \
           parse_number(opening_wip) - \
           parse_number(closing_wip)


def calc_cost_of_goods_sold(opening_stock: float,
                            purchases: float,
                            direct_expenses: float,
                            closing_stock: float) -> float:
    """
    COGS = Opening Stock + Purchases + Direct Expenses - Closing Stock
    """
    return parse_number(opening_stock) + \
           parse_number(purchases) + \
           parse_number(direct_expenses) - \
           parse_number(closing_stock)


def calc_gross_profit(sales: float, cogs: float) -> float:
    """
    Gross Profit = Sales - COGS
    """
    return parse_number(sales) - parse_number(cogs)


def calc_net_profit(gross_profit: float, 
                    other_income: float, 
                    total_expenses: float) -> float:
    """
    Net Profit = Gross Profit + Other Income - Total Expenses
    """
    return parse_number(gross_profit) + \
           parse_number(other_income) - \
           parse_number(total_expenses)


def calc_total_assets(current_assets: float, 
                      fixed_assets: float, 
                      other_assets: float = 0) -> float:
    """Total Assets = Current + Fixed + Other"""
    return parse_number(current_assets) + \
           parse_number(fixed_assets) + \
           parse_number(other_assets)


def calc_total_liabilities(current_liabilities: float,
                           long_term_liabilities: float = 0) -> float:
    """Total Liabilities"""
    return parse_number(current_liabilities) + \
           parse_number(long_term_liabilities)


def calc_capital(opening_capital: float,
                 net_profit: float,
                 drawings: float) -> float:
    """
    Closing Capital = Opening Capital + Net Profit - Drawings
    """
    return parse_number(opening_capital) + \
           parse_number(net_profit) - \
           parse_number(drawings)


# ============================================================
# 4. VALIDATION
# ============================================================

def validate_required(value: Any, field_name: str = "Field") -> tuple:
    """
    လိုအပ်သော field စစ်ဆေးခြင်း
    Returns: (is_valid, error_message)
    """
    if value is None or str(value).strip() == "":
        return False, f"{field_name} ဖြည့်ရန် လိုအပ်ပါသည်"
    return True, ""


def validate_number(value: Any, field_name: str = "Field", 
                    allow_negative: bool = True) -> tuple:
    """Number validation"""
    try:
        num = parse_number(value)
        if not allow_negative and num < 0:
            return False, f"{field_name} သည် အနုတ်မဖြစ်ရပါ"
        return True, ""
    except Exception:
        return False, f"{field_name} သည် ဂဏန်းဖြစ်ရပါမည်"


def validate_client_name(name: str) -> tuple:
    """Client name validation"""
    if not name or len(name.strip()) < 2:
        return False, "အမည်သည် အနည်းဆုံး ၂ လုံး ရှိရပါမည်"
    if len(name) > 100:
        return False, "အမည်သည် ၁၀၀ လုံးထက် မကျော်ရပါ"
    return True, ""


# ============================================================
# 5. BALANCE SHEET CHECKS
# ============================================================

def check_balance_sheet_balance(total_assets: float, 
                                total_liabilities: float,
                                total_capital: float) -> dict:
    """
    Balance Sheet ဟုန်းချင်း ကိုက်ညီမှု စစ်ဆေးခြင်း
    
    Accounting Equation: Assets = Liabilities + Capital
    """
    assets = parse_number(total_assets)
    liab_cap = parse_number(total_liabilities) + parse_number(total_capital)
    diff = assets - liab_cap
    
    is_balanced = abs(diff) < 0.01  # 1 ပြားအောက် ကွာဟမှု လက်ခံ
    
    return {
        "total_assets": assets,
        "total_liabilities_and_capital": liab_cap,
        "difference": diff,
        "is_balanced": is_balanced,
        "message": "✓ ဟုန်းချင်း ကိုက်ညီပါသည်" if is_balanced 
                   else f"✗ ကွာဟမှု: {format_currency(diff)} ကျပ်"
    }


# ============================================================
# 6. SESSION STATE HELPERS
# ============================================================

def init_session_state(key: str, default: Any = None):
    """Session state initialize"""
    if key not in st.session_state:
        st.session_state[key] = default


def get_client_id() -> Optional[int]:
    """လက်ရှိ ရွေးချယ်ထားသော client ID"""
    return st.session_state.get("selected_client_id")


def set_client_id(client_id: int):
    """Client ID သတ်မှတ်ခြင်း"""
    st.session_state["selected_client_id"] = client_id


def clear_client_selection():
    """Client ရွေးချယ်မှု ဖျက်ခြင်း"""
    st.session_state.pop("selected_client_id", None)


# ============================================================
# 7. MISC HELPERS
# ============================================================

def safe_divide(numerator: float, denominator: float, default: float = 0) -> float:
    """Zero division ကာကွယ်ခြင်း"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """စာသား ဖြတ်တောက်ခြင်း"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def generate_filename(prefix: str, client_name: str, 
                      statement_type: str, ext: str = "pdf") -> str:
    """
    PDF filename generate လုပ်ခြင်း
    
    Example:
        generate_filename("FS", "ABC Co", "Manufacturing", "pdf")
        -> 'FS_ABC_Co_Manufacturing_20240315.pdf'
    """
    # Clean client name (remove special chars)
    clean_name = re.sub(r'[^\w\s-]', '', client_name).strip().replace(' ', '_')
    clean_type = re.sub(r'[^\w\s-]', '', statement_type).strip().replace(' ', '_')
    date_str = datetime.now().strftime("%Y%m%d")
    
    return f"{prefix}_{clean_name}_{clean_type}_{date_str}.{ext}"


def print_header(title: str, subtitle: str = ""):
    """Streamlit page header (tablet-friendly, large font)"""
    st.markdown(
        f"""
        <div style="padding: 1rem 0;">
            <h1 style="color: #1f4788; font-size: 2.2rem; margin-bottom: 0.3rem;">
                {title}
            </h1>
            {f'<p style="color: #666; font-size: 1.1rem;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def info_box(message: str, box_type: str = "info"):
    """Colored info box (tablet-friendly)"""
    colors = {
        "info": ("#e3f2fd", "#1565c0", "ℹ️"),
        "success": ("#e8f5e9", "#2e7d32", "✓"),
        "warning": ("#fff3e0", "#e65100", "⚠️"),
        "error": ("#ffebee", "#c62828", "✗"),
    }
    bg, fg, icon = colors.get(box_type, colors["info"])
    
    st.markdown(
        f"""
        <div style="
            background-color: {bg};
            color: {fg};
            padding: 1rem 1.2rem;
            border-radius: 8px;
            border-left: 5px solid {fg};
            font-size: 1.1rem;
            margin: 0.5rem 0;
        ">
            <strong>{icon}</strong> {message}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 8. CONSTANTS
# ============================================================

CURRENCY_SYMBOL = "ကျပ်"
DEFAULT_DECIMALS = 2
BALANCE_TOLERANCE = 0.01

STATEMENT_TYPES = {
    "manufacturing": "ကုန်ထုတ်လုပ်မှု စာရင်း (Manufacturing Account)",
    "trading_pl": "အရောင်းအဝယ် အမြတ်အစွန်း စာရင်း (Trading & P&L)",
    "balance_sheet": "ငွေစာရင်း လက်ကျန်စာရင်း (Balance Sheet)",
}

# ============================================================
# 9. QUICK TEST
# ============================================================

if __name__ == "__main__":
    # Number formatting tests
    print("=== Number Formatting ===")
    print(format_number(1234567.5))           # 1,234,567.50
    print(format_currency(1234567.5, show_unit=True))  # 1,234,567.50 ကျပ်
    print(format_myanmar_currency(150000))    # 1.50 သိန်း
    print(format_myanmar_currency(25000000))  # 2.50 သန်း
    print(parse_number("1,234,567.50"))       # 1234567.5
    
    # Date tests
    print("\n=== Date Formatting ===")
    print(format_date_mm(date(2024, 3, 15)))  # 15 မတ် 2024
    print(format_date_en(date(2024, 3, 15)))  # 2024-03-15
    
    # Calculation tests
    print("\n=== Calculations ===")
    pc = calc_prime_cost(100000, 50000, 10000)
    print(f"Prime Cost: {format_currency(pc)}")  # 160,000.00
    
    prod_cost = calc_production_cost(pc, 30000, 5000, 8000)
    print(f"Production Cost: {format_currency(prod_cost)}")  # 187,000.00
    
    # Balance check
    print("\n=== Balance Sheet Check ===")
    result = check_balance_sheet_balance(500000, 200000, 300000)
    print(result["message"])  # ✓ ဟုန်းချင်း ကိုက်ညီပါသည်
    
    result2 = check_balance_sheet_balance(500000, 200000, 250000)
    print(result2["message"])  # ✗ ကွာဟမှု: 50,000.00 ကျပ်