# core/pdf_generator.py
import os
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from weasyprint import HTML, CSS

from core.utils import (
    format_number, format_date_mm, parse_number
)
from core.templates import merge_template_with_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_REGULAR = os.path.join(BASE_DIR, "assets", "fonts", "pyidaungsu-regular.ttf")
FONT_BOLD = os.path.join(BASE_DIR, "assets", "fonts", "pyidaungsu-bold.ttf")

# ============================================================
# PDF TRANSLATIONS
# ============================================================
PDF_TRANSLATIONS = {
    "my": {
        "period_end": "ကာလကုန်",
        "as_at_date": "ရက်စွဲ",
        "manufacturing_title": "ကုန်ထုတ်လုပ်မှု စာရင်း (Manufacturing Account)",
        "trading_pl_title": "အရောင်းအဝယ် အမြတ်အစွန်း စာရင်း (Trading & P&L)",
        "balance_sheet_title": "ငွေစာရင်း လက်ကျန်စာရင်း (Balance Sheet)",
        "cash_flow_title": "ငွေသား စီးဆင်းမှု ရှင်းတမ်း (Cash Flow Statement)",
        
        # Manufacturing
        "m1": "၁။ တိုက်ရိုက် ကုန်ကြမ်းများ",
        "opening_stock_raw": "အဖွင့် ကုန်ကြမ်းလက်ကျန်",
        "purchases_raw": "ကုန်ကြမ်းဝယ်ယူမှု",
        "carriage_inward": "သယ်ယူပို့ဆောင်ခ",
        "customs_duty": "အကောက်ခွန်",
        "closing_stock_raw": "အပိတ် ကုန်ကြမ်းလက်ကျန်",
        "cost_of_materials_used": "အသုံးပြုသော ကုန်ကြမ်းကုန်ကျစရိတ်",
        "m2": "၂။ တိုက်ရိုက် အလုပ်သမားခ",
        "wages_direct": "တိုက်ရိုက် အလုပ်သမားခ",
        "wages_overtime": "အချိန်ပို အလုပ်သမားခ",
        "wages_contract": "စာချုပ် အလုပ်သမားခ",
        "direct_labour_total": "တိုက်ရိုက် အလုပ်သမားခ စုစုပေါင်း",
        "m3": "၃။ တိုက်ရိုက် အသုံးစရိတ်များ",
        "royalty": "မူပိုင်ခွင့်ကြေး",
        "hire_plant": "စက်ပစ္စည်း ငှားရမ်းခ",
        "fuel_power_direct": "လောင်စာနှင့် လျှပ်စစ်",
        "direct_expenses_total": "တိုက်ရိုက် အသုံးစရိတ် စုစုပေါင်း",
        "prime_cost": "အခြေခံ ကုန်ကျစရိတ် (Prime Cost)",
        "m4": "၄။ စက်ရုံ အသုံးစရိတ်များ",
        "factory_rent": "စက်ရုံ ငှားရမ်းခ",
        "factory_rates": "စက်ရုံ အခွန်",
        "factory_insurance": "စက်ရုံ အာမခံ",
        "factory_power": "စက်ရုံ လျှပ်စစ်",
        "factory_salary": "စက်ရုံ ဝန်ထမ်းခ",
        "depreciation_plant": "စက်ပစ္စည်း တန်ဖိုးကျဆင်း",
        "repairs_plant": "စက်ပစ္စည်း ပြုပြင်ခ",
        "indirect_wages": "သွယ်ဝိုက် အလုပ်သမားခ",
        "factory_misc": "အထွေထွေ စက်ရုံစရိတ်",
        "factory_overhead_total": "စက်ရုံ အသုံးစရိတ် စုစုပေါင်း",
        "m5": "၅။ လုပ်ငန်း ဆောင်ရွက်ဆဲ (WIP)",
        "add_opening_wip": "အဖွင့် WIP",
        "less_closing_wip": "အပိတ် WIP",
        "production_cost": "ကုန်ထုတ်လုပ်မှု ကုန်ကျစရိတ် (Production Cost)",
        
        # Trading
        "trading_acc_title": "က။ အရောင်းအဝယ် စာရင်း (Trading Account)",
        "cash_sales": "ငွေသား အရောင်း",
        "credit_sales": "အကြွေး အရောင်း",
        "less_sales_return": "အရောင်းပြန်အမ်း နုတ်",
        "net_sales": "အရောင်း စုစုပေါင်း (Net Sales)",
        "opening_stock_finished": "အဖွင့် ကုန်ချောလက်ကျန်",
        "add_purchases": "ဝယ်ယူမှု ပေါင်း",
        "add_manufacturing_cost": "ကုန်ထုတ်လုပ်မှု ကုန်ကျစရိတ် ပေါင်း",
        "add_carriage_inward": "သယ်ယူပို့ဆောင်ခ ပေါင်း",
        "add_duty": "အကောက်ခွန် ပေါင်း",
        "less_purchase_return": "ဝယ်ယူမှု ပြန်အမ်း နုတ်",
        "less_closing_stock": "အပိတ် ကုန်ချောလက်ကျန် နုတ်",
        "cogs_total": "COGS စုစုပေါင်း",
        "gross_profit": "အမြတ် (Gross Profit)",
        "pl_acc_title": "ခ။ အမြတ်အစွန်း စာရင်း (Profit & Loss Account)",
        "start_with_gp": "အမြတ် (Gross Profit) ဖြင့် စတင်",
        "other_income": "အခြား ဝင်ငွေများ",
        "other_income_total": "အခြား ဝင်ငွေ စုစုပေါင်း",
        "expenses": "အသုံးစရိတ်များ",
        "expenses_total": "အသုံးစရိတ် စုစုပေါင်း",
        "net_profit": "အသားတင် အမြတ် (Net Profit)",
        
        # Balance Sheet
        "bs_assets_title": "ပိုင်ဆိုင်မှုများ (ASSETS)",
        "bs_ca_title": "၁။ လက်ရှိ ပိုင်ဆိုင်မှုများ",
        "ca_inventories": "ကုန်ပစ္စည်းလက်ကျန်",
        "ca_receivable": "ရရန်ကျန်ငွေ",
        "ca_advance": "ကြိုတင်ပေးငွေ",
        "ca_cash": "လက်ထဲ/ဘဏ် ငွေသား",
        "current_assets_total": "လက်ရှိ ပိုင်ဆိုင်မှု စုစုပေါင်း",
        "bs_fa_title": "၂။ ပုံသေ ပိုင်ဆိုင်မှုများ",
        "nca_land": "မြေ",
        "nca_building": "အဆောက်အအုံ",
        "nca_machine": "စက်ပစ္စည်း",
        "nca_furniture": "ပရိဘောဂ",
        "nca_vehicle": "ယာဉ်",
        "less_depreciation": "တန်ဖိုးကျဆင်းမှု နုတ်",
        "fixed_assets_total": "ပုံသေ ပိုင်ဆိုင်မှု စုစုပေါင်း",
        "total_assets": "ပိုင်ဆိုင်မှု စုစုပေါင်း (TOTAL ASSETS)",
        "bs_liab_title": "အကြွေးများ (LIABILITIES)",
        "bs_cl_title": "၁။ လက်ရှိ အကြွေးများ",
        "liab_payable": "ပေးရန်ကျန်ငွေ",
        "liab_bank_loan": "ဘဏ် ချေးငွေ",
        "current_liabilities_total": "လက်ရှိ အကြွေး စုစုပေါင်း",
        "total_liabilities": "အကြွေး စုစုပေါင်း",
        "bs_cap_title": "အရင်း ငွေ (CAPITAL)",
        "eq_capital": "အရင်း",
        "eq_retain": "စုဆောင်း အမြတ်",
        "eq_profit": "ယခုနှစ် အမြတ်",
        "eq_drawing": "ပိုင်ရှင် ထုတ်ယူမှု",
        "capital_total": "အရင်း စုစုပေါင်း",
        "liabilities_and_capital": "အကြွေးနှင့် အရင်း စုစုပေါင်း",
        "balanced_msg": "✓ ဟုန်းချင်း ကိုက်ညီပါသည် (Assets = Liabilities + Capital)",
        "not_balanced_msg": "✗ ကွာဟမှု: {} ကျပ်",
        
        # Cash Flow
        "cf_op_title": "က။ လုပ်ငန်း လည်ပတ်မှု လုပ်ဆောင်ချက်များမှ ငွေသား",
        "cf_net_profit": "အခွန်မဆိုင်မီ အသားတင် အမြတ်/အရှုံး",
        "cf_depreciation": "တန်ဖိုးကျဆင်းမှု (Depreciation)",
        "cf_op_profit": "လုပ်ငန်းလည်ပတ်မှု အမြတ် (Working Capital မဆိုင်မီ)",
        "cf_inv_change": "ကုန်ပစ္စည်းလက်ကျန် တိုး/ကျ",
        "cf_rec_change": "ရရန်ကျန်ငွေ တိုး/ကျ",
        "cf_pay_change": "ပေးရန်ကျန်ငွေ တိုး/ကျ",
        "cf_net_op": "လုပ်ငန်းလည်ပတ်မှုမှ ရရှိသော ငွေသား (Net)",
        "cf_inv_title": "ခ။ ရင်းနှီးမြှုပ်နှံမှု လုပ်ဆောင်ချက်များမှ ငွေသား",
        "cf_invest_fa": "ပုံသေပိုင်ဆိုင်မှု ဝယ်ယူမှု",
        "cf_net_investing": "ရင်းနှီးမြှုပ်နှံမှုမှ ထွက်သွားသော ငွေသား (Net)",
        "cf_fin_title": "ဂ။ ငွေကြေးရှာဖွေမှု လုပ်ဆောင်ချက်များမှ ငွေသား",
        "cf_fin_loan": "ချေးငွေ တိုးလာမှု",
        "cf_fin_draw": "ပိုင်ရှင် ထုတ်ယူမှု (Drawing)",
        "cf_net_financing": "ငွေကြေးရှာဖွေမှုမှ ထွက်သွားသော ငွေသား (Net)",
        "cf_summary_title": "ငွေသား အကျဉ်းချုပ်",
        "cf_net_change": "ငွေသား ပြောင်းလဲမှု (Net Change)",
        "cf_opening_cash": "ကာလအစ ငွေသား",
        "cf_closing_cash": "ကာလအဆုံး ငွေသား",
    },
    "en": {
        "period_end": "Period End",
        "as_at_date": "As at Date",
        "manufacturing_title": "Manufacturing Account",
        "trading_pl_title": "Trading and Profit & Loss Account",
        "balance_sheet_title": "Balance Sheet",
        "cash_flow_title": "Cash Flow Statement",
        
        # Manufacturing
        "m1": "1. Direct Materials",
        "opening_stock_raw": "Opening Stock (Raw)",
        "purchases_raw": "Purchases (Raw)",
        "carriage_inward": "Carriage Inward",
        "customs_duty": "Customs Duty",
        "closing_stock_raw": "Closing Stock (Raw)",
        "cost_of_materials_used": "Cost of Materials Used",
        "m2": "2. Direct Labour",
        "wages_direct": "Direct Wages",
        "wages_overtime": "Overtime Wages",
        "wages_contract": "Contract Wages",
        "direct_labour_total": "Total Direct Labour",
        "m3": "3. Direct Expenses",
        "royalty": "Royalty",
        "hire_plant": "Hire of Plant",
        "fuel_power_direct": "Fuel & Power",
        "direct_expenses_total": "Total Direct Expenses",
        "prime_cost": "Prime Cost",
        "m4": "4. Factory Overhead",
        "factory_rent": "Factory Rent",
        "factory_rates": "Factory Rates",
        "factory_insurance": "Factory Insurance",
        "factory_power": "Factory Power",
        "factory_salary": "Factory Salary",
        "depreciation_plant": "Depreciation - Plant",
        "repairs_plant": "Repairs - Plant",
        "indirect_wages": "Indirect Wages",
        "factory_misc": "Misc Factory Exp",
        "factory_overhead_total": "Total Factory Overhead",
        "m5": "5. Work in Progress",
        "add_opening_wip": "Opening WIP",
        "less_closing_wip": "Closing WIP",
        "production_cost": "Production Cost",
        
        # Trading
        "trading_acc_title": "A. Trading Account",
        "cash_sales": "Cash Sales",
        "credit_sales": "Credit Sales",
        "less_sales_return": "Less: Sales Returns",
        "net_sales": "Net Sales",
        "opening_stock_finished": "Opening Stock (Finished)",
        "add_purchases": "Add: Purchases",
        "add_manufacturing_cost": "Add: Manufacturing Cost",
        "add_carriage_inward": "Add: Carriage Inward",
        "add_duty": "Add: Customs Duty",
        "less_purchase_return": "Less: Purchase Returns",
        "less_closing_stock": "Less: Closing Stock",
        "cogs_total": "Total COGS",
        "gross_profit": "Gross Profit",
        "pl_acc_title": "B. Profit & Loss Account",
        "start_with_gp": "Start with Gross Profit",
        "other_income": "Other Income",
        "other_income_total": "Total Other Income",
        "expenses": "Expenses",
        "expenses_total": "Total Expenses",
        "net_profit": "Net Profit",
        
        # Balance Sheet
        "bs_assets_title": "ASSETS",
        "bs_ca_title": "1. Current Assets",
        "ca_inventories": "Inventories",
        "ca_receivable": "A/C Receivable",
        "ca_advance": "Advance Payments",
        "ca_cash": "Cash",
        "current_assets_total": "Total Current Assets",
        "bs_fa_title": "2. Fixed Assets",
        "nca_land": "Land",
        "nca_building": "Building",
        "nca_machine": "Machine",
        "nca_furniture": "Furniture",
        "nca_vehicle": "Vehicle",
        "less_depreciation": "Less: Depreciation",
        "fixed_assets_total": "Total Fixed Assets",
        "total_assets": "TOTAL ASSETS",
        "bs_liab_title": "LIABILITIES",
        "bs_cl_title": "1. Current Liabilities",
        "liab_payable": "A/C Payable",
        "liab_bank_loan": "Bank Loan",
        "current_liabilities_total": "Total Current Liabilities",
        "total_liabilities": "TOTAL LIABILITIES",
        "bs_cap_title": "CAPITAL",
        "eq_capital": "Capital",
        "eq_retain": "Retain Earning",
        "eq_profit": "Profit for the year",
        "eq_drawing": "Drawing",
        "capital_total": "Total Capital",
        "liabilities_and_capital": "TOTAL LIABILITIES & CAPITAL",
        "balanced_msg": "✓ Balanced (Assets = Liabilities + Capital)",
        "not_balanced_msg": "✗ Difference: {} Kyats",
        
        # Cash Flow
        "cf_op_title": "A. CASH FLOW FROM OPERATION ACTIVITIES",
        "cf_net_profit": "Net Profit before Taxation",
        "cf_depreciation": "Depreciation",
        "cf_op_profit": "Operation Profit before Working Capital",
        "cf_inv_change": "Changes in Inventories",
        "cf_rec_change": "Changes in A/C Receivable",
        "cf_pay_change": "Changes in Creditors",
        "cf_net_op": "Net cash inflow from Operation",
        "cf_inv_title": "B. CASH FLOW FROM INVESTING ACTIVITIES",
        "cf_invest_fa": "Purchase of Fixed Assets",
        "cf_net_investing": "Net Cash from Investing",
        "cf_fin_title": "C. CASH FLOW FROM FINANCING ACTIVITIES",
        "cf_fin_loan": "Increase in Loan",
        "cf_fin_draw": "Drawing",
        "cf_net_financing": "Net Cash from Financing",
        "cf_summary_title": "CASH SUMMARY",
        "cf_net_change": "Net Change in Cash",
        "cf_opening_cash": "Cash at Beginning",
        "cf_closing_cash": "Cash at End",
    }
}

def get_pdf_text(lang: str, key: str) -> str:
    return PDF_TRANSLATIONS.get(lang, PDF_TRANSLATIONS["my"]).get(key, key)


# ============================================================
# 1. CALCULATION ENGINE
# ============================================================

def calculate_manufacturing(data: Dict[str, Any]) -> Dict[str, Any]:
    t = merge_template_with_data("manufacturing", data)
    dm = t["direct_materials"]["items"]
    cost_of_materials_used = (parse_number(dm["opening_stock_raw"]["value"]) + parse_number(dm["purchases_raw"]["value"]) + parse_number(dm["carriage_inward"]["value"]) + parse_number(dm["customs_duty"]["value"]) - parse_number(dm["closing_stock_raw"]["value"]))
    t["direct_materials"]["cost_of_materials_used"] = cost_of_materials_used
    
    dl = t["direct_labour"]["items"]
    direct_labour_total = (parse_number(dl["wages_direct"]["value"]) + parse_number(dl["wages_overtime"]["value"]) + parse_number(dl["wages_contract"]["value"]))
    t["direct_labour"]["direct_labour_total"] = direct_labour_total
    
    de = t["direct_expenses"]["items"]
    direct_expenses_total = (parse_number(de["royalty"]["value"]) + parse_number(de["hire_plant"]["value"]) + parse_number(de["fuel_power_direct"]["value"]))
    t["direct_expenses"]["direct_expenses_total"] = direct_expenses_total
    
    prime_cost = cost_of_materials_used + direct_labour_total + direct_expenses_total
    t["prime_cost"]["value"] = prime_cost
    
    fo = t["factory_overhead"]["items"]
    factory_overhead_total = sum(parse_number(item["value"]) for item in fo.values())
    t["factory_overhead"]["factory_overhead_total"] = factory_overhead_total
    
    wip = t["work_in_progress"]["items"]
    opening_wip = parse_number(wip["add_opening_wip"]["value"])
    closing_wip = parse_number(wip["less_closing_wip"]["value"])
    
    production_cost = prime_cost + factory_overhead_total + opening_wip - closing_wip
    t["production_cost"]["value"] = production_cost
    t["transfer_to_trading"]["value"] = production_cost
    return t

def calculate_trading_pl(data: Dict[str, Any]) -> Dict[str, Any]:
    t = merge_template_with_data("trading_pl", data)
    sales = t["trading"]["sales"]["items"]
    net_sales = (parse_number(sales["cash_sales"]["value"]) + parse_number(sales["credit_sales"]["value"]) - parse_number(sales["less_sales_return"]["value"]))
    t["trading"]["sales"]["net_sales"] = net_sales
    
    cogs = t["trading"]["cogs"]["items"]
    cogs_total = (parse_number(cogs["opening_stock_finished"]["value"]) + parse_number(cogs["add_purchases"]["value"]) + parse_number(cogs["add_manufacturing_cost"]["value"]) + parse_number(cogs["add_carriage_inward"]["value"]) + parse_number(cogs["add_duty"]["value"]) - parse_number(cogs["less_purchase_return"]["value"]) - parse_number(cogs["less_closing_stock"]["value"]))
    t["trading"]["cogs"]["cogs_total"] = cogs_total
    
    gross_profit = net_sales - cogs_total
    t["trading"]["gross_profit"]["value"] = gross_profit
    
    oi = t["profit_loss"]["other_income"]["items"]
    other_income_total = sum(parse_number(item["value"]) for item in oi.values())
    t["profit_loss"]["other_income"]["other_income_total"] = other_income_total
    
    ex = t["profit_loss"]["expenses"]["items"]
    expenses_total = sum(parse_number(item["value"]) for item in ex.values())
    t["profit_loss"]["expenses"]["expenses_total"] = expenses_total
    
    net_profit = gross_profit + other_income_total - expenses_total
    t["profit_loss"]["net_profit"]["value"] = net_profit
    return t

def calculate_balance_sheet(data: Dict[str, Any]) -> Dict[str, Any]:
    t = merge_template_with_data("balance_sheet", data)
    
    ca = t["assets"]["current_assets"]["items"]
    current_assets_total = sum(parse_number(item["value"]) for item in ca.values())
    t["assets"]["current_assets"]["current_assets_total"] = current_assets_total
    
    fa = t["assets"]["fixed_assets"]["items"]
    fixed_assets_total = (sum(parse_number(v["value"]) for k, v in fa.items() if not v.get("is_deduction", False)) - parse_number(fa["less_depreciation"]["value"]))
    t["assets"]["fixed_assets"]["fixed_assets_total"] = fixed_assets_total
    
    total_assets = current_assets_total + fixed_assets_total
    t["assets"]["total_assets"]["value"] = total_assets
    
    cl = t["liabilities"]["current_liabilities"]["items"]
    current_liabilities_total = sum(parse_number(item["value"]) for item in cl.values())
    t["liabilities"]["current_liabilities"]["current_liabilities_total"] = current_liabilities_total
    
    total_liabilities = current_liabilities_total
    t["liabilities"]["total_liabilities"]["value"] = total_liabilities
    
    cap = t["capital"]["items"]
    capital_total = (parse_number(cap["eq_capital"]["value"]) + parse_number(cap["eq_retain"]["value"]) + parse_number(cap["eq_profit"]["value"]) - parse_number(cap["eq_drawing"]["value"]))
    t["capital"]["capital_total"] = capital_total
    
    liab_cap = total_liabilities + capital_total
    t["balance_check"]["liabilities_and_capital"]["value"] = liab_cap
    diff = total_assets - liab_cap
    t["balance_check"]["difference"] = diff
    t["balance_check"]["is_balanced"] = abs(diff) < 0.01
    return t

# ============================================================
# 2. HTML RENDER HELPERS
# ============================================================

def _build_html_header(client_name: str, title: str, period_str: str) -> str:
    return f"""
    <div class="header">
        <h1>{client_name}</h1>
        <h2>{title}</h2>
        <p class="period">{period_str}</p>
    </div>
    """

def _build_html_row(label: str, value: float, is_subtotal=False, is_total=False, is_deduction=False, is_bold=False):
    if is_subtotal: css_class = "subtotal-row"
    elif is_total: css_class = "total-row"
    else: css_class = ""
    
    amount_str = format_number(value, decimals=2)
    if is_deduction:
        amount_str = f"({amount_str})"
        
    label_style = "font-weight: bold;" if is_bold else ""
        
    return f"""
    <tr class="{css_class}">
        <td class="label" style="{label_style}">{label}</td>
        <td class="amount">{amount_str}</td>
    </tr>
    """

def _render_manufacturing_html(t: Dict[str, Any], lang: str) -> str:
    html = ""
    dm = t["direct_materials"]
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "m1")}</td></tr>'
    html += _build_html_row(get_pdf_text(lang, "opening_stock_raw"), dm["items"]["opening_stock_raw"]["value"])
    html += _build_html_row(get_pdf_text(lang, "purchases_raw"), dm["items"]["purchases_raw"]["value"])
    html += _build_html_row(get_pdf_text(lang, "carriage_inward"), dm["items"]["carriage_inward"]["value"])
    html += _build_html_row(get_pdf_text(lang, "customs_duty"), dm["items"]["customs_duty"]["value"])
    html += _build_html_row(get_pdf_text(lang, "closing_stock_raw"), dm["items"]["closing_stock_raw"]["value"], is_deduction=True)
    html += _build_html_row(get_pdf_text(lang, "cost_of_materials_used"), dm["cost_of_materials_used"], is_subtotal=True)
    
    dl = t["direct_labour"]
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "m2")}</td></tr>'
    for k in ["wages_direct", "wages_overtime", "wages_contract"]:
        html += _build_html_row(get_pdf_text(lang, k), dl["items"][k]["value"])
    html += _build_html_row(get_pdf_text(lang, "direct_labour_total"), dl["direct_labour_total"], is_subtotal=True)
    
    de = t["direct_expenses"]
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "m3")}</td></tr>'
    for k in ["royalty", "hire_plant", "fuel_power_direct"]:
        html += _build_html_row(get_pdf_text(lang, k), de["items"][k]["value"])
    html += _build_html_row(get_pdf_text(lang, "direct_expenses_total"), de["direct_expenses_total"], is_subtotal=True)
    
    html += _build_html_row(get_pdf_text(lang, "prime_cost"), t["prime_cost"]["value"], is_total=True)
    
    fo = t["factory_overhead"]
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "m4")}</td></tr>'
    for k, item in fo["items"].items():
        html += _build_html_row(get_pdf_text(lang, k), item["value"])
    html += _build_html_row(get_pdf_text(lang, "factory_overhead_total"), fo["factory_overhead_total"], is_subtotal=True)
    
    wip = t["work_in_progress"]["items"]
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "m5")}</td></tr>'
    html += _build_html_row(get_pdf_text(lang, "add_opening_wip"), wip["add_opening_wip"]["value"])
    html += _build_html_row(get_pdf_text(lang, "less_closing_wip"), wip["less_closing_wip"]["value"], is_deduction=True)
    
    html += _build_html_row(get_pdf_text(lang, "production_cost"), t["production_cost"]["value"], is_total=True)
    return html

def _render_trading_pl_html(t: Dict[str, Any], lang: str) -> str:
    html = ""
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "trading_acc_title")}</td></tr>'
    sales = t["trading"]["sales"]["items"]
    html += _build_html_row(get_pdf_text(lang, "cash_sales"), sales["cash_sales"]["value"])
    html += _build_html_row(get_pdf_text(lang, "credit_sales"), sales["credit_sales"]["value"])
    html += _build_html_row(get_pdf_text(lang, "less_sales_return"), sales["less_sales_return"]["value"], is_deduction=True)
    html += _build_html_row(get_pdf_text(lang, "net_sales"), t["trading"]["sales"]["net_sales"], is_subtotal=True)
    
    cogs = t["trading"]["cogs"]["items"]
    html += _build_html_row(get_pdf_text(lang, "opening_stock_finished"), cogs["opening_stock_finished"]["value"])
    html += _build_html_row(get_pdf_text(lang, "add_purchases"), cogs["add_purchases"]["value"])
    html += _build_html_row(get_pdf_text(lang, "add_manufacturing_cost"), cogs["add_manufacturing_cost"]["value"])
    html += _build_html_row(get_pdf_text(lang, "add_carriage_inward"), cogs["add_carriage_inward"]["value"])
    html += _build_html_row(get_pdf_text(lang, "add_duty"), cogs["add_duty"]["value"])
    html += _build_html_row(get_pdf_text(lang, "less_purchase_return"), cogs["less_purchase_return"]["value"], is_deduction=True)
    html += _build_html_row(get_pdf_text(lang, "less_closing_stock"), cogs["less_closing_stock"]["value"], is_deduction=True)
    html += _build_html_row(get_pdf_text(lang, "cogs_total"), t["trading"]["cogs"]["cogs_total"], is_subtotal=True)
    
    gp = t["trading"]["gross_profit"]
    gp_label = get_pdf_text(lang, "gross_profit") if gp["value"] >= 0 else ("အရှုံး" if lang=="my" else "Gross Loss")
    html += _build_html_row(gp_label, gp["value"], is_total=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "pl_acc_title")}</td></tr>'
    html += _build_html_row(get_pdf_text(lang, "start_with_gp"), gp["value"], is_bold=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "other_income")}</td></tr>'
    oi = t["profit_loss"]["other_income"]["items"]
    for k, item in oi.items(): 
        html += _build_html_row(item["label_mm"] if lang=="my" else item["label_en"], item["value"])
    html += _build_html_row(get_pdf_text(lang, "other_income_total"), t["profit_loss"]["other_income"]["other_income_total"], is_subtotal=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "expenses")}</td></tr>'
    ex = t["profit_loss"]["expenses"]["items"]
    for k, item in ex.items(): 
        html += _build_html_row(item["label_mm"] if lang=="my" else item["label_en"], item["value"])
    html += _build_html_row(get_pdf_text(lang, "expenses_total"), t["profit_loss"]["expenses"]["expenses_total"], is_subtotal=True)
    
    np_ = t["profit_loss"]["net_profit"]
    np_label = get_pdf_text(lang, "net_profit") if np_["value"] >= 0 else ("အသားတင် အရှုံး" if lang=="my" else "Net Loss")
    html += _build_html_row(np_label, np_["value"], is_total=True)
    return html

def _render_balance_sheet_html(t: Dict[str, Any], lang: str) -> str:
    html = ""
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "bs_assets_title")}</td></tr>'
    
    html += f'<tr class="sub-section"><td colspan="2">{get_pdf_text(lang, "bs_ca_title")}</td></tr>'
    ca = t["assets"]["current_assets"]["items"]
    for k, item in ca.items(): 
        html += _build_html_row(get_pdf_text(lang, k), item["value"])
    html += _build_html_row(get_pdf_text(lang, "current_assets_total"), t["assets"]["current_assets"]["current_assets_total"], is_subtotal=True)
    
    html += f'<tr class="sub-section"><td colspan="2">{get_pdf_text(lang, "bs_fa_title")}</td></tr>'
    fa = t["assets"]["fixed_assets"]["items"]
    for k, item in fa.items():
        is_ded = item.get("is_deduction", False)
        html += _build_html_row(get_pdf_text(lang, k), item["value"], is_deduction=is_ded)
    html += _build_html_row(get_pdf_text(lang, "fixed_assets_total"), t["assets"]["fixed_assets"]["fixed_assets_total"], is_subtotal=True)
    
    html += _build_html_row(get_pdf_text(lang, "total_assets"), t["assets"]["total_assets"]["value"], is_total=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "bs_liab_title")}</td></tr>'
    html += f'<tr class="sub-section"><td colspan="2">{get_pdf_text(lang, "bs_cl_title")}</td></tr>'
    cl = t["liabilities"]["current_liabilities"]["items"]
    for k, item in cl.items(): 
        html += _build_html_row(get_pdf_text(lang, k), item["value"])
    html += _build_html_row(get_pdf_text(lang, "current_liabilities_total"), t["liabilities"]["current_liabilities"]["current_liabilities_total"], is_subtotal=True)
    
    html += _build_html_row(get_pdf_text(lang, "total_liabilities"), t["liabilities"]["total_liabilities"]["value"], is_total=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "bs_cap_title")}</td></tr>'
    cap = t["capital"]["items"]
    html += _build_html_row(get_pdf_text(lang, "eq_capital"), cap["eq_capital"]["value"])
    html += _build_html_row(get_pdf_text(lang, "eq_retain"), cap["eq_retain"]["value"])
    html += _build_html_row(get_pdf_text(lang, "eq_profit"), cap["eq_profit"]["value"])
    html += _build_html_row(get_pdf_text(lang, "eq_drawing"), cap["eq_drawing"]["value"], is_deduction=True)
    html += _build_html_row(get_pdf_text(lang, "capital_total"), t["capital"]["capital_total"], is_subtotal=True)
    
    html += _build_html_row(get_pdf_text(lang, "liabilities_and_capital"), t["balance_check"]["liabilities_and_capital"]["value"], is_total=True)
    
    diff = t["balance_check"]["difference"]
    is_balanced = t["balance_check"]["is_balanced"]
    if is_balanced:
        msg = get_pdf_text(lang, "balanced_msg")
        css_class = "balanced"
    else:
        msg = get_pdf_text(lang, "not_balanced_msg").format(format_number(diff, 2))
        css_class = "not-balanced"
        
    html += f'<tr class="{css_class}"><td colspan="2" style="text-align:center; font-weight:bold; padding: 10px;">{msg}</td></tr>'
    return html

def _render_cash_flow_html(data: Dict[str, Any], lang: str) -> str:
    html = ""
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "cf_op_title")}</td></tr>'
    net_profit = parse_number(data.get("net_profit", 0))
    dep = parse_number(data.get("depreciation", 0))
    html += _build_html_row(get_pdf_text(lang, "cf_net_profit"), net_profit)
    html += _build_html_row(get_pdf_text(lang, "cf_depreciation"), dep)
    
    op_profit = net_profit + dep
    html += _build_html_row(get_pdf_text(lang, "cf_op_profit"), op_profit, is_subtotal=True)
    
    inv_chg = -parse_number(data.get("change_inventories", 0))
    rec_chg = -parse_number(data.get("change_receivable", 0))
    pay_chg = parse_number(data.get("change_payable", 0))
    wc_chg = inv_chg + rec_chg + pay_chg
    if inv_chg != 0: html += _build_html_row(get_pdf_text(lang, "cf_inv_change"), inv_chg, is_deduction=(inv_chg < 0))
    if rec_chg != 0: html += _build_html_row(get_pdf_text(lang, "cf_rec_change"), rec_chg, is_deduction=(rec_chg < 0))
    if pay_chg != 0: html += _build_html_row(get_pdf_text(lang, "cf_pay_change"), pay_chg, is_deduction=(pay_chg < 0))
    
    net_op = op_profit + wc_chg
    html += _build_html_row(get_pdf_text(lang, "cf_net_op"), net_op, is_total=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "cf_inv_title")}</td></tr>'
    invest_fa = -parse_number(data.get("investing_purchase_fa", 0))
    if invest_fa != 0: html += _build_html_row(get_pdf_text(lang, "cf_invest_fa"), invest_fa, is_deduction=True)
    html += _build_html_row(get_pdf_text(lang, "cf_net_investing"), invest_fa, is_total=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "cf_fin_title")}</td></tr>'
    fin_loan = parse_number(data.get("financing_loan_increase", 0))
    fin_draw = -parse_number(data.get("financing_drawing", 0))
    if fin_loan != 0: html += _build_html_row(get_pdf_text(lang, "cf_fin_loan"), fin_loan)
    if fin_draw != 0: html += _build_html_row(get_pdf_text(lang, "cf_fin_draw"), fin_draw, is_deduction=True)
    net_fin = fin_loan + fin_draw
    html += _build_html_row(get_pdf_text(lang, "cf_net_financing"), net_fin, is_total=True)
    
    html += f'<tr class="section-header"><td colspan="2">{get_pdf_text(lang, "cf_summary_title")}</td></tr>'
    net_chg = net_op + invest_fa + net_fin
    open_cash = parse_number(data.get("opening_cash", 0))
    close_cash = open_cash + net_chg
    html += _build_html_row(get_pdf_text(lang, "cf_net_change"), net_chg, is_subtotal=True)
    html += _build_html_row(get_pdf_text(lang, "cf_opening_cash"), open_cash)
    html += _build_html_row(get_pdf_text(lang, "cf_closing_cash"), close_cash, is_total=True)
    
    return html

# ============================================================
# 3. MAIN PUBLIC API
# ============================================================

def generate_pdf(statement_type: str, client_name: str, 
                 data: Dict[str, Any], period_end: str = "", 
                 as_at_date: str = "", 
                 output_path: Optional[str] = None,
                 lang: str = "my") -> bytes:
    
    titles = {
        "manufacturing": get_pdf_text(lang, "manufacturing_title"),
        "trading_pl":    get_pdf_text(lang, "trading_pl_title"),
        "balance_sheet": get_pdf_text(lang, "balance_sheet_title"),
        "cash_flow":     get_pdf_text(lang, "cash_flow_title"),
    }
    
    if statement_type not in titles:
        raise ValueError(f"မသိသော statement type: {statement_type}")

    if statement_type == "manufacturing":
        data["period_end"] = period_end
        t_res = calculate_manufacturing(data)
        period_str = f"{get_pdf_text(lang, 'period_end')}: {format_date_mm(period_end)}"
        table_html = _render_manufacturing_html(t_res, lang)
    elif statement_type == "trading_pl":
        data["period_end"] = period_end
        t_res = calculate_trading_pl(data)
        period_str = f"{get_pdf_text(lang, 'period_end')}: {format_date_mm(period_end)}"
        table_html = _render_trading_pl_html(t_res, lang)
    elif statement_type == "balance_sheet":
        data["as_at_date"] = as_at_date
        t_res = calculate_balance_sheet(data)
        period_str = f"{get_pdf_text(lang, 'as_at_date')}: {format_date_mm(as_at_date)}"
        table_html = _render_balance_sheet_html(t_res, lang)
    elif statement_type == "cash_flow":
        data["period_end"] = period_end
        period_str = f"{get_pdf_text(lang, 'period_end')}: {format_date_mm(period_end)}"
        table_html = _render_cash_flow_html(data, lang)
    
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @font-face {{
                font-family: 'Pyidaungsu';
                src: url('file://{FONT_REGULAR}');
                font-weight: normal;
            }}
            @font-face {{
                font-family: 'Pyidaungsu';
                src: url('file://{FONT_BOLD}');
                font-weight: bold;
            }}
            
            @page {{
                size: A4 portrait;
                margin: 15mm;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Pyidaungsu';
                    font-size: 8pt;
                    color: #777;
                }}
                @bottom-left {{
                    content: "Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}";
                    font-family: 'Pyidaungsu';
                    font-size: 8pt;
                    color: #777;
                }}
            }}
            
            body {{
                font-family: 'Pyidaungsu', sans-serif;
                font-size: 10pt;
                color: #212121;
            }}
            
            .header {{ text-align: center; margin-bottom: 15px; }}
            .header h1 {{ font-size: 16pt; font-weight: bold; color: #1f4788; margin: 0; }}
            .header h2 {{ font-size: 13pt; font-weight: bold; margin: 5px 0 0 0; }}
            .header .period {{ font-size: 10pt; color: #666; margin-top: 5px; }}
            
            hr {{ border: 1px solid #1f4788; margin-bottom: 10px; }}
            
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 4px 8px; }}
            .label {{ text-align: left; }}
            .amount {{ text-align: right; }}
            
            .section-header td {{
                background-color: #e3f2fd; color: #1565c0; font-weight: bold;
                padding-top: 8px; padding-bottom: 8px;
                border-top: 1px solid #90caf9; border-bottom: 1px solid #90caf9;
            }}
            
            .sub-section td {{
                font-weight: bold; color: #333; padding-top: 6px; padding-bottom: 6px;
            }}
            
            .subtotal-row td {{
                background-color: #f5f5f5; font-weight: bold; border-top: 1px solid #ddd;
            }}
            
            .total-row td {{
                background-color: #fff3e0; color: #e65100; font-weight: bold; font-size: 11pt;
                border-top: 2px solid #e65100; border-bottom: 2px solid #e65100;
            }}
            
            .balanced td {{ color: #2e7d32; background-color: #e8f5e9; }}
            .not-balanced td {{ color: #c62828; background-color: #ffebee; }}
        </style>
    </head>
    <body>
        {_build_html_header(client_name, titles[statement_type], period_str)}
        <hr>
        <table>
            {table_html}
        </table>
    </body>
    </html>
    """
    
    pdf_bytes = HTML(string=full_html).write_pdf()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
            
    return pdf_bytes