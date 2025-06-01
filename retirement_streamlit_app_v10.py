import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Retirement Planner", layout="wide")

st.title("💼 Retirement Income Estimator")

# --- Input Fields ---
col1, col2 = st.columns(2)

with col1:
    dob = st.date_input(
        "Your Date of Birth",
        value=datetime.date(1977, 8, 17),
        min_value=datetime.date(1900, 1, 1),
        max_value=datetime.date.today()
    )
    retirement_date = st.date_input(
        "Planned Retirement Date",
        value=datetime.date(2032, 8, 17)
    )
    current_pension_pot = st.number_input(
        "Current Pension Pot (£)", value=61000
    )
    monthly_pension_contribution = st.number_input(
        "Monthly Pension Contribution (£)", value=2100
    )
    pension_growth_rate = st.slider(
        "Expected Annual Pension Growth Rate (%)", 1, 12, 7
    ) / 100
    raf_pension_annual = st.number_input(
        "RAF Pension at Retirement (£/year)", value=20000
    )
    dividends_annual = st.number_input(
        "Annual Dividend Income (£)", value=6000
    )

with col2:
    current_isa_pot = st.number_input(
        "Current ISA Pot (£)", value=20000
    )
    monthly_isa_contribution = st.number_input(
        "Monthly ISA Contribution (£)", value=1000
    )
    isa_growth_rate = st.slider(
        "Expected Annual ISA Growth Rate (%)", 1, 12, 7
    ) / 100
    current_house_value = st.number_input(
        "Current House Value (£)", value=530000
    )
    future_house_price = st.number_input(
        "Target Downsized House Price (£)", value=350000
    )
    mortgage_outstanding = st.number_input(
        "Mortgage Outstanding at Retirement (£)", value=155000
    )

# --- Helper Function ---
def future_value(present_value, monthly_contribution, annual_rate, months):
    """
    Compound a present value plus monthly contributions over a number of months,
    using a given annual_rate (e.g. 0.07 for 7%).
    """
    if months <= 0:
        return present_value
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1
    # FV of initial lump sum
    fv_lump = present_value * (1 + monthly_rate) ** months
    # FV of monthly contributions (annuity formula)
    if monthly_rate != 0:
        fv_series = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    else:
        fv_series = monthly_contribution * months
    return fv_lump + fv_series

# --- Calculations ---
today = datetime.date.today()
age_today = relativedelta(today, dob).years
age_at_retirement = relativedelta(retirement_date, dob).years

# Calculate months between today and retirement_date
months_to_retirement = (retirement_date.year - today.year) * 12 + (retirement_date.month - today.month)
if retirement_date.day < today.day:
    # If the day of month is earlier, subtract one month
    months_to_retirement -= 1

# Pension pot at retirement
pension_pot_at_retirement = future_value(
    present_value=current_pension_pot,
    monthly_contribution=monthly_pension_contribution,
    annual_rate=pension_growth_rate,
    months=months_to_retirement
)

# ISA pot at retirement
isa_pot_at_retirement = future_value(
    present_value=current_isa_pot,
    monthly_contribution=monthly_isa_contribution,
    annual_rate=isa_growth_rate,
    months=months_to_retirement
)

# Equity released at retirement
equity_released = max(
    current_house_value - future_house_price - mortgage_outstanding,
    0
)

# Total drawdown base
total_drawdown_base = pension_pot_at_retirement + isa_pot_at_retirement + equity_released

# 4% drawdown income
drawdown_income = total_drawdown_base * 0.04

# Calculate tax on RAF pension
# RAF pension: first £12,500 + additional £3,500 tax-free
tax_free_thr = 12500 + 3500
taxable_raf = max(0, raf_pension_annual - tax_free_thr)
tax_due_raf = taxable_raf * 0.20
net_raf = raf_pension_annual - tax_due_raf

# ISA drawdown is tax-free; dividends are assumed taxable at 20%; pension drawdown taxed at 20%
taxable_drawdown = drawdown_income
taxable_dividends = dividends_annual
tax_due_drawdown = taxable_drawdown * 0.20
tax_due_dividends = taxable_dividends * 0.20

total_tax = tax_due_raf + tax_due_drawdown + tax_due_dividends

# Net income
gross_income = drawdown_income + raf_pension_annual + dividends_annual
net_income = gross_income - total_tax
monthly_net_income = net_income / 12

# --- Display Results ---
st.markdown(f"""
<h2 style="color:white;">Estimated Retirement at Age {age_at_retirement}</h2>
<h1 style="color:green;">£{net_income:,.0f} per year</h1>
<h3 style="color:white;">Monthly Net Income:</h3> <h2 style="color:green;">£{monthly_net_income:,.0f}</h2>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 🔍 Retirement Pot Details")
st.markdown(f"<span style='color:white;'>Pension Pot at Retirement:</span> <span style='color:green;'>£{pension_pot_at_retirement:,.0f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='color:white;'>ISA Pot at Retirement:</span> <span style='color:green;'>£{isa_pot_at_retirement:,.0f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='color:white;'>Equity Released:</span> <span style='color:green;'>£{equity_released:,.0f}</span>", unsafe_allow_html=True)

st.caption("This tool assumes fixed growth rates and simplified tax rules. For personalized advice, consult a financial adviser.")
