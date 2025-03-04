import numpy as np
import numpy_financial as npf

def calculate_financials(
    purchase_price,
    down_payment_pr,       # As decimal (0.2 for 20%)
    loan_term,
    interest_rate,          # As decimal (0.07 for 7%)
    monthly_rent,
    vacancy_rate,           # As decimal (0.05 for 5%)
    property_tax,
    insurance_cost,
    maintenance_cost,
    management_fees,        # As decimal (0.1 for 10%)
    inflation_rate,         # As decimal (0.04 for 4%)
    risk_premium,           # As decimal (0.05 for 5%)
    appreciation_rate,      # As decimal (0.03 for 3%)
    selling_costs=0.05,     # As decimal (5% selling costs)
    interest_rate_shock=0.01,  # As decimal (1% shock)
):
    # Convert annual rates to monthly where needed
    monthly_interest_rate = interest_rate / 12
    num_payments = loan_term * 12

    # --- Loan Calculations ---
    down_payment = purchase_price * down_payment_pr
    loan_amount = purchase_price - down_payment
    
    # Mortgage payment using numpy financial
    mortgage_payment = -npf.pmt(
        monthly_interest_rate,
        num_payments,
        loan_amount
    )
    
    # --- Cash Flow Calculations ---
    # Annual rental income (net of vacancy)
    annual_rent = monthly_rent * 12 * (1 - vacancy_rate)
    
    # Annual expenses
    total_expenses = (
        property_tax
        + insurance_cost
        + maintenance_cost
        + (annual_rent * management_fees)
    )
    
    # Net Operating Income
    net_operating_income = annual_rent - total_expenses
    
    # Annual mortgage payments
    annual_mortgage_payment = mortgage_payment * 12
    
    # Cash flow before taxes
    cashflow = net_operating_income - annual_mortgage_payment
    
    # --- Return Metrics ---
    # Cap rate calculation
    cap_rate = net_operating_income / purchase_price
    
    # Cash on cash return
    cash_on_cash_return = cashflow / down_payment
    
    # --- IRR/NPV with Terminal Value ---
    # Project future property value
    future_value = purchase_price * (1 + appreciation_rate) ** loan_term
    net_proceeds = future_value * (1 - selling_costs)  # After selling costs
    
    # Create cash flow array
    cashflows = [-down_payment] + [cashflow] * (loan_term - 1) + [cashflow + net_proceeds]
    
    # Calculate IRR/NPV
    try:
        internal_rate_of_return = npf.irr(cashflows)
    except:
        internal_rate_of_return = np.nan
    
    net_present_value = npf.npv(risk_premium, cashflows)
    
    # --- Debt Metrics ---
    # Calculate total interest paid
    total_principal = loan_amount
    total_payments = mortgage_payment * num_payments
    total_interest = total_payments - total_principal
    
    # First year interest calculation
    per_period_principal = npf.ppmt(
        monthly_interest_rate,
        np.arange(1, 13),
        num_payments,
        loan_amount
    )
    per_period_interest = npf.ipmt(
        monthly_interest_rate,
        np.arange(1, 13),
        num_payments,
        loan_amount
    )
    first_year_interest = abs(sum(per_period_interest))
    
    # --- Risk Metrics ---
    # Stress test calculations
    stressed_rate = interest_rate + interest_rate_shock
    stressed_payment = -npf.pmt(
        stressed_rate/12,
        num_payments,
        loan_amount
    )
    
    return {
        # Core metrics
        'down_payment': down_payment,
        'loan_amount': loan_amount,
        'monthly_payment': mortgage_payment,
        'annual_mortgage': annual_mortgage_payment,
        
        # Returns
        'cash_on_cash': cash_on_cash_return,
        'cap_rate': cap_rate,
        'irr': internal_rate_of_return,
        'npv': net_present_value,
        
        # Debt analysis
        'total_interest': total_interest,
        'first_year_interest': first_year_interest,
        'dscr': net_operating_income / annual_mortgage_payment,
        'stressed_dscr': net_operating_income / (stressed_payment * 12),
        
        # Property value
        'appreciated_value': future_value,
        'net_sale_proceeds': net_proceeds,
        
        # Ratios
        'ltv': loan_amount / purchase_price,
        'rent_yield': annual_rent / purchase_price,
    }

# Example Usage
if __name__ == "__main__":
    results = calculate_financials(
        purchase_price=1_000_000,
        down_payment_pr=0.20,
        loan_term=25,
        interest_rate=0.07,
        monthly_rent=5_000,
        vacancy_rate=0.05,
        property_tax=5_000,
        insurance_cost=1_000,
        maintenance_cost=2_000,
        management_fees=0.10,
        inflation_rate=0.04,
        risk_premium=0.05,
        appreciation_rate=0.03,
    )
    
    # Format output
    for k, v in results.items():
        if isinstance(v, float):
            print(f"{k:25}: {v:10.2%}" if 'rate' in k else f"{k:25}: {v:10,.2f}")