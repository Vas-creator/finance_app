# core/templates.py
"""
Accounting App - Financial Statement Templates
ဘဏ္ဍာရေး ရှင်းတမ်း ၃ ခုအတွက် Template များ

Statements:
  1. Manufacturing Account  — ကုန်ထုတ်လုပ်မှု စာရင်း
  2. Trading & Profit/Loss  — အရောင်းအဝယ် အမြတ်အစွန်း
  3. Balance Sheet          — ငွေစာရင်း လက်ကျန်စာရင်း

Author: [Your Name]
For: Retired Account Officer (Dad)
"""

from typing import Dict, List, Any, Optional
from copy import deepcopy


# ============================================================
# 1. MANUFACTURING ACCOUNT TEMPLATE
# ============================================================

MANUFACTURING_TEMPLATE: Dict[str, Any] = {
    "statement_type": "manufacturing",
    "title_mm": "ကုန်ထုတ်လုပ်မှု စာရင်း",
    "title_en": "Manufacturing Account",
    "period_end": "",
    
    # ---------- Direct Materials ----------
    "direct_materials": {
        "label_mm": "ကုန်ကြမ်းများ",
        "label_en": "Direct Materials",
        "items": {
            "opening_stock_raw": {"label_mm": "အဖွင့် ကုန်ကြမ်းလက်ကျန်", "label_en": "Opening Stock of Raw Materials", "value": 0.0},
            "purchases_raw":     {"label_mm": "ကုန်ကြမ်းဝယ်ယူမှု",        "label_en": "Purchases of Raw Materials",    "value": 0.0},
            "carriage_inward":   {"label_mm": "သယ်ယူပို့ဆောင်ခ",          "label_en": "Carriage Inward",               "value": 0.0},
            "customs_duty":      {"label_mm": "အကောက်ခွန်",               "label_en": "Customs Duty",                  "value": 0.0},
            "closing_stock_raw": {"label_mm": "အပိတ် ကုန်ကြမ်းလက်ကျန်",  "label_en": "Closing Stock of Raw Materials", "value": 0.0, "is_deduction": True},
        },
        "subtotal_key": "cost_of_materials_used",
        "subtotal_mm": "အသုံးပြုသော ကုန်ကြမ်းကုန်ကျစရိတ်",
        "subtotal_en": "Cost of Materials Used",
    },
    
    # ---------- Direct Labour ----------
    "direct_labour": {
        "label_mm": "တိုက်ရိုက် အလုပ်သမားခ",
        "label_en": "Direct Labour",
        "items": {
            "wages_direct":      {"label_mm": "တိုက်ရိုက် အလုပ်သမားခ",    "label_en": "Direct Wages",                  "value": 0.0},
            "wages_overtime":    {"label_mm": "အချိန်ပို အလုပ်သမားခ",      "label_en": "Overtime Wages",                "value": 0.0},
            "wages_contract":    {"label_mm": "စာချုပ် အလုပ်သမားခ",        "label_en": "Contract Labour",               "value": 0.0},
        },
        "subtotal_key": "direct_labour_total",
        "subtotal_mm": "တိုက်ရိုက် အလုပ်သမားခ စုစုပေါင်း",
        "subtotal_en": "Total Direct Labour",
    },
    
    # ---------- Direct Expenses ----------
    "direct_expenses": {
        "label_mm": "တိုက်ရိုက် အသုံးစရိတ်များ",
        "label_en": "Direct Expenses",
        "items": {
            "royalty":           {"label_mm": "မူပိုင်ခွင့်ကြေး",          "label_en": "Royalty on Production",        "value": 0.0},
            "hire_plant":        {"label_mm": "စက်ပစ္စည်း ငှားရမ်းခ",       "label_en": "Hire of Plant",                "value": 0.0},
            "fuel_power_direct": {"label_mm": "လောင်စာနှင့် လျှပ်စစ်",     "label_en": "Fuel & Power (Direct)",        "value": 0.0},
        },
        "subtotal_key": "direct_expenses_total",
        "subtotal_mm": "တိုက်ရိုက် အသုံးစရိတ် စုစုပေါင်း",
        "subtotal_en": "Total Direct Expenses",
    },
    
    # ---------- PRIME COST ----------
    "prime_cost": {
        "label_mm": "အခြေခံ ကုန်ကျစရိတ် (Prime Cost)",
        "label_en": "PRIME COST",
        "value": 0.0,
        "is_calculated": True,
        "formula": "cost_of_materials_used + direct_labour_total + direct_expenses_total",
    },
    
    # ---------- Factory Overhead ----------
    "factory_overhead": {
        "label_mm": "စက်ရုံ အသုံးစရိတ်များ",
        "label_en": "Factory Overhead",
        "items": {
            "factory_rent":       {"label_mm": "စက်ရုံ ငှားရမ်းခ",         "label_en": "Factory Rent",                  "value": 0.0},
            "factory_rates":      {"label_mm": "စက်ရုံ အခွန်",             "label_en": "Factory Rates & Taxes",         "value": 0.0},
            "factory_insurance":  {"label_mm": "စက်ရုံ အာမခံ",             "label_en": "Factory Insurance",             "value": 0.0},
            "factory_power":      {"label_mm": "စက်ရုံ လျှပ်စစ်",          "label_en": "Factory Power & Light",         "value": 0.0},
            "factory_salary":     {"label_mm": "စက်ရုံ ဝန်ထမ်းခ",           "label_en": "Factory Salaries",              "value": 0.0},
            "depreciation_plant": {"label_mm": "စက်ပစ္စည်း တန်ဖိုးကျဆင်း", "label_en": "Depreciation - Plant",          "value": 0.0},
            "repairs_plant":      {"label_mm": "စက်ပစ္စည်း ပြုပြင်ခ",       "label_en": "Repairs to Plant",              "value": 0.0},
            "indirect_wages":     {"label_mm": "သွယ်ဝိုက် အလုပ်သမားခ",    "label_en": "Indirect Wages",                "value": 0.0},
            "factory_misc":       {"label_mm": "အထွေထွေ စက်ရုံစရိတ်",     "label_en": "Miscellaneous Factory Expenses", "value": 0.0},
        },
        "subtotal_key": "factory_overhead_total",
        "subtotal_mm": "စက်ရုံ အသုံးစရိတ် စုစုပေါင်း",
        "subtotal_en": "Total Factory Overhead",
    },
    
    # ---------- Work in Progress ----------
    "work_in_progress": {
        "label_mm": "လုပ်ငန်း ဆောင်ရွက်ဆဲ",
        "label_en": "Work in Progress",
        "items": {
            "add_opening_wip":    {"label_mm": "အဖွင့် WIP",  "label_en": "Add: Opening WIP",     "value": 0.0, "is_addition": True},
            "less_closing_wip":   {"label_mm": "အပိတ် WIP",   "label_en": "Less: Closing WIP",    "value": 0.0, "is_deduction": True},
        },
    },
    
    # ---------- PRODUCTION COST ----------
    "production_cost": {
        "label_mm": "ကုန်ထုတ်လုပ်မှု ကုန်ကျစရိတ် (Production Cost)",
        "label_en": "PRODUCTION COST",
        "value": 0.0,
        "is_calculated": True,
        "formula": "prime_cost + factory_overhead_total + add_opening_wip - less_closing_wip",
    },
    
    # ---------- Transfer to Trading ----------
    "transfer_to_trading": {
        "label_mm": "အရောင်းအဝယ်စာရင်းသို့ လွှဲပြောင်း",
        "label_en": "Transfer to Trading Account",
        "value": 0.0,
        "is_calculated": True,
        "formula": "production_cost",
    },
}


# ============================================================
# 2. TRADING & PROFIT/LOSS TEMPLATE
# ============================================================

TRADING_PL_TEMPLATE: Dict[str, Any] = {
    "statement_type": "trading_pl",
    "title_mm": "အရောင်းအဝယ် အမြတ်အစွန်း စာရင်း",
    "title_en": "Trading and Profit & Loss Account",
    "period_end": "",
    
    # ---------- TRADING ACCOUNT ----------
    "trading": {
        "label_mm": "အရောင်းအဝယ် စာရင်း",
        "label_en": "Trading Account",
        
        "sales": {
            "label_mm": "အရောင်းများ",
            "label_en": "Sales",
            "items": {
                "cash_sales":         {"label_mm": "ငွေသား အရောင်း",          "label_en": "Cash Sales",              "value": 0.0},
                "credit_sales":       {"label_mm": "အကြွေး အရောင်း",          "label_en": "Credit Sales",            "value": 0.0},
                "less_sales_return":  {"label_mm": "အရောင်းပြန်အမ်း",         "label_en": "Less: Sales Returns",     "value": 0.0, "is_deduction": True},
            },
            "subtotal_key": "net_sales",
            "subtotal_mm": "အရောင်း စုစုပေါင်း (Net Sales)",
            "subtotal_en": "Net Sales",
        },
        
        "cogs": {
            "label_mm": "ရောင်းချသော ကုန်ပစ္စည်း ကုန်ကျစရိတ်",
            "label_en": "Cost of Goods Sold",
            "items": {
                "opening_stock_finished": {"label_mm": "အဖွင့် ကုန်ချောလက်ကျန်",  "label_en": "Opening Stock - Finished Goods", "value": 0.0},
                "add_purchases":          {"label_mm": "ဝယ်ယူမှု",                 "label_en": "Add: Purchases",                 "value": 0.0},
                "add_manufacturing_cost": {"label_mm": "ကုန်ထုတ်လုပ်မှု ကုန်ကျစရိတ်", "label_en": "Add: Manufacturing Cost",     "value": 0.0},
                "add_carriage_inward":    {"label_mm": "သယ်ယူပို့ဆောင်ခ",           "label_en": "Add: Carriage Inward",          "value": 0.0},
                "add_duty":               {"label_mm": "အကောက်ခွန်",                 "label_en": "Add: Customs Duty",             "value": 0.0},
                "less_purchase_return":   {"label_mm": "ဝယ်ယူမှု ပြန်အမ်း",         "label_en": "Less: Purchase Returns",         "value": 0.0, "is_deduction": True},
                "less_closing_stock":     {"label_mm": "အပိတ် ကုန်ချောလက်ကျန်",    "label_en": "Less: Closing Stock - Finished", "value": 0.0, "is_deduction": True},
            },
            "subtotal_key": "cogs_total",
            "subtotal_mm": "COGS စုစုပေါင်း",
            "subtotal_en": "Total COGS",
        },
        
        "gross_profit": {
            "label_mm": "အမြတ် (Gross Profit)",
            "label_en": "GROSS PROFIT",
            "value": 0.0,
            "is_calculated": True,
            "formula": "net_sales - cogs_total",
            "if_negative_label_mm": "အရှုံး (Gross Loss)",
            "if_negative_label_en": "GROSS LOSS",
        },
    },
    
    # ---------- PROFIT & LOSS ----------
    "profit_loss": {
        "label_mm": "အမြတ်အစွန်း စာရင်း",
        "label_en": "Profit & Loss Account",
        
        "other_income": {
            "label_mm": "အခြား ဝင်ငွေများ",
            "label_en": "Other Income",
            "items": {
                "discount_received":  {"label_mm": "လျှော့စျေး ရရှိမှု",       "label_en": "Discount Received",     "value": 0.0},
                "commission_received":{"label_mm": "ကော်မရှင် ရရှိမှု",        "label_en": "Commission Received",   "value": 0.0},
                "interest_received":  {"label_mm": "အတိုး ရရှိမှု",            "label_en": "Interest Received",     "value": 0.0},
                "rent_received":      {"label_mm": "ငှားရမ်းခ ရရှိမှု",         "label_en": "Rent Received",         "value": 0.0},
                "bad_debt_recovered": {"label_mm": "မရရှိသော အကြွေး ပြန်ရ",   "label_en": "Bad Debts Recovered",   "value": 0.0},
                "misc_income":        {"label_mm": "အထွေထွေ ဝင်ငွေ",          "label_en": "Miscellaneous Income",  "value": 0.0},
            },
            "subtotal_key": "other_income_total",
            "subtotal_mm": "အခြား ဝင်ငွေ စုစုပေါင်း",
            "subtotal_en": "Total Other Income",
        },
        
        "expenses": {
            "label_mm": "အသုံးစရိတ်များ",
            "label_en": "Expenses",
            "items": {
                "office_salary":     {"label_mm": "ရုံး ဝန်ထမ်းခ",          "label_en": "Office Salaries",           "value": 0.0},
                "office_rent":       {"label_mm": "ရုံး ငှားရမ်းခ",          "label_en": "Office Rent",               "value": 0.0},
                "office_rates":      {"label_mm": "ရုံး အခွန်",              "label_en": "Office Rates & Taxes",      "value": 0.0},
                "office_insurance":  {"label_mm": "ရုံး အာမခံ",              "label_en": "Office Insurance",          "value": 0.0},
                "office_power":      {"label_mm": "ရုံး လျှပ်စစ်နှင့်ရေ",    "label_en": "Office Power & Water",      "value": 0.0},
                "printing_stationery":{"label_mm": "စာရေးကိရိယာ",           "label_en": "Printing & Stationery",     "value": 0.0},
                "postage_telephone": {"label_mm": "စာပို့နှင့် တယ်လီဖုန်း",  "label_en": "Postage & Telephone",       "value": 0.0},
                "travel_conveyance": {"label_mm": "ခရီးသွား စရိတ်",         "label_en": "Travel & Conveyance",       "value": 0.0},
                "advertisement":     {"label_mm": "ကြော်ငြာ စရိတ်",         "label_en": "Advertisement",             "value": 0.0},
                "legal_professional":{"label_mm": "ဥပဒေ အကြံပေးခ",         "label_en": "Legal & Professional Fees", "value": 0.0},
                "audit_fees":        {"label_mm": "စာရင်းစစ် ကြေး",         "label_en": "Audit Fees",                "value": 0.0},
                "bank_charges":      {"label_mm": "ဘဏ် ဝန်ဆောင်ခ",          "label_en": "Bank Charges",              "value": 0.0},
                "interest_paid":     {"label_mm": "အတိုး ပေးရမှု",           "label_en": "Interest Paid",             "value": 0.0},
                "depreciation_office":{"label_mm": "ရုံးပစ္စည်း တန်ဖိုးကျဆင်း","label_en": "Depreciation - Office",   "value": 0.0},
                "bad_debts":         {"label_mm": "မရရှိသော အကြွေး",        "label_en": "Bad Debts Written Off",     "value": 0.0},
                "misc_expenses":     {"label_mm": "အထွေထွေ စရိတ်",          "label_en": "Miscellaneous Expenses",    "value": 0.0},
            },
            "subtotal_key": "expenses_total",
            "subtotal_mm": "အသုံးစရိတ် စုစုပေါင်း",
            "subtotal_en": "Total Expenses",
        },
        
        "net_profit": {
            "label_mm": "အသားတင် အမြတ် (Net Profit)",
            "label_en": "NET PROFIT",
            "value": 0.0,
            "is_calculated": True,
            "formula": "gross_profit + other_income_total - expenses_total",
            "if_negative_label_mm": "အသားတင် အရှုံး (Net Loss)",
            "if_negative_label_en": "NET LOSS",
        },
    },
}


# ============================================================
# 3. BALANCE SHEET TEMPLATE
# ============================================================

BALANCE_SHEET_TEMPLATE: Dict[str, Any] = {
    "statement_type": "balance_sheet",
    "title_mm": "ငွေစာရင်း လက်ကျန်စာရင်း",
    "title_en": "Balance Sheet",
    "as_at_date": "",
    
    "assets": {
        "label_mm": "ပိုင်ဆိုင်မှုများ",
        "label_en": "ASSETS",
        "current_assets": {
            "label_mm": "လက်ရှိ ပိုင်ဆိုင်မှုများ",
            "label_en": "Current Assets",
            "items": {
                "ca_inventories": {"label_mm": "ကုန်ပစ္စည်းလက်ကျန်", "label_en": "Inventories", "value": 0.0},
                "ca_receivable": {"label_mm": "ရရန်ကျန်ငွေ", "label_en": "A/C Receivable", "value": 0.0},
                "ca_advance": {"label_mm": "ကြိုတင်ပေးငွေ", "label_en": "Advance Payments", "value": 0.0},
                "ca_cash": {"label_mm": "လက်ထဲ/ဘဏ် ငွေသား", "label_en": "Cash", "value": 0.0},
            },
            "subtotal_key": "current_assets_total",
            "subtotal_mm": "လက်ရှိ ပိုင်ဆိုင်မှု စုစုပေါင်း",
            "subtotal_en": "Total Current Assets",
        },
        "fixed_assets": {
            "label_mm": "ပုံသေ ပိုင်ဆိုင်မှုများ",
            "label_en": "Fixed Assets",
            "items": {
                "nca_land": {"label_mm": "မြေ", "label_en": "Land", "value": 0.0},
                "nca_building": {"label_mm": "အဆောက်အအုံ", "label_en": "Building", "value": 0.0},
                "nca_machine": {"label_mm": "စက်ပစ္စည်း", "label_en": "Machine", "value": 0.0},
                "nca_furniture": {"label_mm": "ပရိဘောဂ", "label_en": "Furniture", "value": 0.0},
                "nca_vehicle": {"label_mm": "ယာဉ်", "label_en": "Vehicle", "value": 0.0},
                "less_depreciation": {"label_mm": "တန်ဖိုးကျဆင်းမှု နုတ်", "label_en": "Less: Depreciation", "value": 0.0, "is_deduction": True},
            },
            "subtotal_key": "fixed_assets_total",
            "subtotal_mm": "ပုံသေ ပိုင်ဆိုင်မှု စုစုပေါင်း",
            "subtotal_en": "Total Fixed Assets",
        },
        "total_assets": {
            "label_mm": "ပိုင်ဆိုင်မှု စုစုပေါင်း",
            "label_en": "TOTAL ASSETS",
            "value": 0.0,
            "is_calculated": True,
            "formula": "current_assets_total + fixed_assets_total",
        },
    },
    
    "liabilities": {
        "label_mm": "အကြွေးများ",
        "label_en": "LIABILITIES",
        "current_liabilities": {
            "label_mm": "လက်ရှိ အကြွေးများ",
            "label_en": "Current Liabilities",
            "items": {
                "liab_payable": {"label_mm": "ပေးရန်ကျန်ငွေ", "label_en": "A/C Payable", "value": 0.0},
                "liab_bank_loan": {"label_mm": "ဘဏ် ချေးငွေ", "label_en": "Bank Loan", "value": 0.0},
            },
            "subtotal_key": "current_liabilities_total",
            "subtotal_mm": "လက်ရှိ အကြွေး စုစုပေါင်း",
            "subtotal_en": "Total Current Liabilities",
        },
        "total_liabilities": {
            "label_mm": "အကြွေး စုစုပေါင်း",
            "label_en": "TOTAL LIABILITIES",
            "value": 0.0,
            "is_calculated": True,
            "formula": "current_liabilities_total",
        },
    },
    
    "capital": {
        "label_mm": "အရင်း ငွေ",
        "label_en": "CAPITAL",
        "items": {
            "eq_capital": {"label_mm": "အရင်း", "label_en": "Capital", "value": 0.0},
            "eq_retain": {"label_mm": "စုဆောင်း အမြတ်", "label_en": "Retain Earning", "value": 0.0},
            "eq_profit": {"label_mm": "ယခုနှစ် အမြတ်", "label_en": "Profit for the year", "value": 0.0},
            "eq_drawing": {"label_mm": "ပိုင်ရှင် ထုတ်ယူမှု", "label_en": "Drawing", "value": 0.0, "is_deduction": True},
        },
        "subtotal_key": "capital_total",
        "subtotal_mm": "အရင်း စုစုပေါင်း",
        "subtotal_en": "Total Capital",
    },
    
    "balance_check": {
        "total_assets_key": "total_assets",
        "total_liab_capital_key": "total_liabilities_and_capital",
        "liabilities_and_capital": {
            "label_mm": "အကြွေးနှင့် အရင်း စုစုပေါင်း",
            "label_en": "TOTAL LIABILITIES & CAPITAL",
            "value": 0.0,
            "is_calculated": True,
            "formula": "total_liabilities + capital_total",
        },
        "is_balanced": False,
        "difference": 0.0,
    },
}
    
# ============================================================
# 4. TEMPLATE REGISTRY
# ============================================================

TEMPLATES: Dict[str, Dict[str, Any]] = {
    "manufacturing": MANUFACTURING_TEMPLATE,
    "trading_pl":    TRADING_PL_TEMPLATE,
    "balance_sheet": BALANCE_SHEET_TEMPLATE,
}


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================

def get_template(statement_type: str) -> Dict[str, Any]:
    """Template အသစ် (deep copy) ရယူခြင်း — မူရင်း မပျက်စေရန်"""
    if statement_type not in TEMPLATES:
        raise ValueError(f"မသိသော statement type: {statement_type}")
    return deepcopy(TEMPLATES[statement_type])


def list_statement_types() -> List[Dict[str, str]]:
    """ရရှိနိုင်သော statement type စာရင်း"""
    return [
        {"key": "manufacturing", "label_mm": "ကုန်ထုတ်လုပ်မှု စာရင်း",       "label_en": "Manufacturing Account"},
        {"key": "trading_pl",    "label_mm": "အရောင်းအဝယ် အမြတ်အစွန်း စာရင်း", "label_en": "Trading & Profit/Loss"},
        {"key": "balance_sheet", "label_mm": "ငွေစာရင်း လက်ကျန်စာရင်း",      "label_en": "Balance Sheet"},
    ]


def get_all_line_items(statement_type: str) -> List[Dict[str, str]]:
    """
    Template ထဲမှ line item အားလုံးကို flat list အဖြစ် ရယူခြင်း
    (ဖောင် ဖန်တီးရန် / PDF ရေးရန် အသုံးဝင်သည်)
    
    Returns:
        [
            {"key": "opening_stock_raw", "label_mm": "...", "label_en": "...", "section": "direct_materials", "value": 0.0},
            ...
        ]
    """
    template = get_template(statement_type)
    items = []
    
    def _walk(node: Dict, section_path: str = ""):
        for key, val in node.items():
            if isinstance(val, dict):
                if "label_mm" in val and "value" in val:
                    # Line item တစ်ခု
                    items.append({
                        "key":        key,
                        "label_mm":   val.get("label_mm", ""),
                        "label_en":   val.get("label_en", ""),
                        "section":    section_path or key,
                        "value":      val.get("value", 0.0),
                        "is_deduction": val.get("is_deduction", False),
                        "is_addition":  val.get("is_addition", False),
                        "is_calculated": val.get("is_calculated", False),
                        "subtotal_key": val.get("subtotal_key"),
                    })
                else:
                    # Nested section
                    new_path = f"{section_path}.{key}" if section_path else key
                    _walk(val, new_path)
    
    # Root section တွေကို ဖြတ်သွား
    for root_key, root_val in template.items():
        if root_key in ("statement_type", "title_mm", "title_en", 
                        "period_end", "as_at_date", "balance_check"):
            continue
        if isinstance(root_val, dict):
            _walk(root_val, root_key)
    
    return items


def get_input_fields(statement_type: str) -> List[Dict[str, str]]:
    """
    User ဖြည့်ရမည့် field များ (calculated field များ ဖယ်)
    Streamlit form ဖန်တီးရန် အသုံးဝင်သည်
    """
    all_items = get_all_line_items(statement_type)
    return [item for item in all_items if not item.get("is_calculated", False)]


def validate_template_data(statement_type: str, data: Dict[str, Any]) -> tuple:
    """
    Template data စစ်ဆေးခြင်း
    Returns: (is_valid, errors_list)
    """
    errors = []
    
    if statement_type not in TEMPLATES:
        return False, [f"မသိသော statement type: {statement_type}"]
    
    if not isinstance(data, dict):
        return False, ["Data သည် dictionary ဖြစ်ရပါမည်"]
    
    required_fields = get_input_fields(statement_type)
    for field in required_fields:
        if field["key"] not in data:
            # Default 0 ဖြစ်လျှင် error မထုတ်
            continue
        val = data[field["key"]]
        if val is not None and not isinstance(val, (int, float)):
            try:
                float(val)
            except (ValueError, TypeError):
                errors.append(f"{field['label_mm']} သည် ဂဏန်းဖြစ်ရပါမည်")
    
    return len(errors) == 0, errors


def merge_template_with_data(statement_type: str, 
                             data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Template အသစ်တစ်ခုဖန်တီးပြီး user data နှင့် ပေါင်းခြင်း
    """
    template = get_template(statement_type)
    
    def _apply(node: Dict):
        for key, val in list(node.items()):
            if isinstance(val, dict):
                if "value" in val and key in data:
                    node[key]["value"] = float(data[key]) if data[key] is not None else 0.0
                else:
                    _apply(val)
    
    _apply(template)
    return template


def get_template_summary() -> List[Dict[str, Any]]:
    """Template တစ်ခုချင်းစီရဲ့ အကျဉ်းချုပ်"""
    summary = []
    for st in list_statement_types():
        items = get_input_fields(st["key"])
        summary.append({
            "key":         st["key"],
            "label_mm":    st["label_mm"],
            "label_en":    st["label_en"],
            "input_count": len(items),
        })
    return summary


# ============================================================
# 6. QUICK TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEMPLATES MODULE — QUICK TEST")
    print("=" * 60)
    
    # Test 1: Template summary
    print("\n[1] Statement Types Summary:")
    for s in get_template_summary():
        print(f"  • {s['label_mm']:35} ({s['key']:15}) → {s['input_count']} input fields")
    
    # Test 2: Manufacturing template keys
    print("\n[2] Manufacturing Template — Top-level keys:")
    mfg = get_template("manufacturing")
    for k in mfg.keys():
        print(f"  • {k}")
    
    # Test 3: Input fields (Manufacturing)
    print("\n[3] Manufacturing — Input Fields (ပထမ ၅ ခု):")
    mfg_fields = get_input_fields("manufacturing")
    for f in mfg_fields[:5]:
        print(f"  • {f['key']:25} : {f['label_mm']}")
    print(f"  ... (စုစုပေါင်း {len(mfg_fields)} fields)")
    
    # Test 4: Input fields (Trading & P&L)
    print("\n[4] Trading & P&L — Input Fields (ပထမ ၅ ခု):")
    tpl_fields = get_input_fields("trading_pl")
    for f in tpl_fields[:5]:
        print(f"  • {f['key']:25} : {f['label_mm']}")
    print(f"  ... (စုစုပေါင်း {len(tpl_fields)} fields)")
    
    # Test 5: Input fields (Balance Sheet)
    print("\n[5] Balance Sheet — Input Fields (ပထမ ၅ ခု):")
    bs_fields = get_input_fields("balance_sheet")
    for f in bs_fields[:5]:
        print(f"  • {f['key']:25} : {f['label_mm']}")
    print(f"  ... (စုစုပေါင်း {len(bs_fields)} fields)")
    
    # Test 6: Merge with sample data
    print("\n[6] Merge Test — Sample Manufacturing Data:")
    sample_data = {
        "opening_stock_raw": 100000,
        "purchases_raw": 500000,
        "closing_stock_raw": 80000,
        "wages_direct": 150000,
        "factory_rent": 50000,
    }
    merged = merge_template_with_data("manufacturing", sample_data)
    print(f"  • opening_stock_raw: {merged['direct_materials']['items']['opening_stock_raw']['value']:,.2f}")
    print(f"  • purchases_raw:     {merged['direct_materials']['items']['purchases_raw']['value']:,.2f}")
    print(f"  • factory_rent:      {merged['factory_overhead']['items']['factory_rent']['value']:,.2f}")
    
    # Test 7: Validate
    print("\n[7] Validation Test:")
    is_valid, errors = validate_template_data("manufacturing", sample_data)
    print(f"  • Valid: {is_valid}")
    if errors:
        for e in errors:
            print(f"    - {e}")
    
    # Test 8: All line items count
    print("\n[8] All Line Items Count:")
    for st in ["manufacturing", "trading_pl", "balance_sheet"]:
        items = get_all_line_items(st)
        print(f"  • {st:15} → {len(items)} items (input + calculated)")
    
    print("\n" + "=" * 60)
    print("✓ အားလုံး အောင်မြင်ပါသည်")
    print("=" * 60)