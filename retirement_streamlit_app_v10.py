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
        value=datetime.date(2032, 8, 17),
        min_value=datetime.date.today(),
        max_value=datetime.date(2099, 12, 31)
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
    db_income = st.number_input(
        "DB Income at Payout (£/year)", value=20000
    )
    db_payout_age = st.number_input(
        "Age that DB Scheme Pays Out", min_value=50, max_value=70, value=55
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
    tax_free_allowance = st.number_input(
        "Estimated Tax Free Allowance (£)", value=12500
    )
    dividends_annual = st.number_input(
        "Annual Dividend Income (£)", value=6000
    )

# --- Helper Function ---
def future_value(present_value, monthly_contribution, annual_rate, months):
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1
    fv_lump = present_value * (1 + monthly_rate) ** months
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

# Determine DB income if age >= payout age
db_income_effective = db_income if age_at_retirement >= db_payout_age else 0

# Calculate drawdown incomes separately
pension_drawdown_income = pension_pot_at_retirement * 0.04
isa_drawdown_income = isa_pot_at_retirement * 0.04
equity_drawdown_income = equity_released * 0.04

# Gross incomes by source
gross_pension = pension_drawdown_income
gross_isa = isa_drawdown_income
gross_equity = equity_drawdown_income
gross_db = db_income_effective
gross_dividends = dividends_annual

total_gross_income = gross_pension + gross_isa + gross_equity + gross_db + gross_dividends

# --- Tax Calculation (UK bands) ---
remaining = total_gross_income
tax = 0

# Band 1: 0 - 12,570 at 0%
band1 = min(remaining, 12570)
remaining -= band1

# Band 2: 12,571 - 50,270 at 20%
band2 = min(max(0, total_gross_income - 12570), 50270 - 12570)
tax += band2 * 0.20
remaining -= band2

# Band 3: 50,271 - 125,140 at 40%
band3 = min(max(0, total_gross_income - 50270), 125140 - 50270)
tax += band3 * 0.40
remaining -= band3

# Band 4: above 125,140 at 45%
band4 = max(0, total_gross_income - 125140)
tax += band4 * 0.45

net_income = total_gross_income - tax
monthly_net_income = net_income / 12

# Allocate tax proportionally to each source for net breakdown
proportion_pension = gross_pension / total_gross_income if total_gross_income > 0 else 0
proportion_isa = gross_isa / total_gross_income if total_gross_income > 0 else 0
proportion_equity = gross_equity / total_gross_income if total_gross_income > 0 else 0
proportion_db = gross_db / total_gross_income if total_gross_income > 0 else 0
proportion_dividends = gross_dividends / total_gross_income if total_gross_income > 0 else 0

net_pension = gross_pension - tax * proportion_pension
net_isa = gross_isa - tax * proportion_isa
net_equity = gross_equity - tax * proportion_equity
net_db = gross_db - tax * proportion_db
net_dividends = gross_dividends - tax * proportion_dividends

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
st.markdown(f"<span style='color:white;'>DB Income at Retirement:</span> <span style='color:green;'>£{db_income_effective:,.0f}</span>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 💡 Income Breakdown")
st.markdown(f"<span style='color:white;'>Pension Drawdown (Gross):</span> <span style='color:green;'>£{gross_pension:,.0f}</span> &raquo; <span style='color:green;'>Net: £{net_pension:,.0f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='color:white;'>ISA Drawdown (Gross):</span> <span style='color:green;'>£{gross_isa:,.0f}</span> &raquo; <span style='color:green;'>Net: £{net_isa:,.0f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='color:white;'>Equity Drawdown (Gross):</span> <span style='color:green;'>£{gross_equity:,.0f}</span> &raquo; <span style='color:green;'>Net: £{net_equity:,.0f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='color:white;'>DB Pension (Gross):</span> <span style='color:green;'>£{gross_db:,.0f}</span> &raquo; <span style='color:green;'>Net: £{net_db:,.0f}</span>", unsafe_allow_html=True)
st.markdown(f"<span style='color:white;'>Dividends (Gross):</span> <span style='color:green;'>£{gross_dividends:,.0f}</span> &raquo; <span style='color:green;'>Net: £{net_dividends:,.0f}</span>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 📋 Assumptions")
st.markdown("- All investment growths assumed at 7% annually.\n- Tax calculated on total gross income using UK 2023/24 bands: 0% for £0–£12,570; 20% for £12,571–£50,270; 40% for £50,271–£125,140; 45% above £125,140.")

st.caption("This tool assumes fixed growth rates and simplified tax rules. For personalized advice, consult a financial adviser.")



