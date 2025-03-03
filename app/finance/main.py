import numpy as np
import numpy_financial as npf


def calculate_financials(
    purchase_price,
    down_payment_pr,
    loan_term,
    interest_rate,
    monthly_rent,
    vacancy_rate,
    property_tax,
    insurance_cost,
    maintenance_cost,
    management_fees,
    inflation_rate,
    risk_premium,
    appreciation_rate,
    interest_rate_shock=1.0,  # Percentage increase for stress test
    market_volatility=0.05,  # Hypothetical volatility index
):
    # Loan & Mortgage Calculations
    down_payment = purchase_price * down_payment_pr
    loan_amount = purchase_price - down_payment
    monthly_interest_rate = interest_rate / 100 / 12
    num_payments = loan_term * 12
    mortgage_payment = (loan_amount * monthly_interest_rate) / (
        1 - (1 + monthly_interest_rate) ** -num_payments
    )

    # Rental Income
    annual_rent = monthly_rent * 12 * (1 - vacancy_rate)
    rental_yield = (annual_rent / purchase_price) * 100
    gross_rent_multiplier = purchase_price / annual_rent
    price_to_rent_ratio = purchase_price / annual_rent

    # Expenses
    total_expenses = (
        property_tax
        + insurance_cost
        + maintenance_cost
        + (management_fees * annual_rent)
    )

    # Profitability
    net_operating_income = annual_rent - total_expenses
    annual_mortgage_payment = mortgage_payment * 12
    cashflow = net_operating_income - annual_mortgage_payment
    cap_rate = (net_operating_income / purchase_price) * 100
    cash_on_cash_return = (cashflow / down_payment) * 100

    # Risk & Return Metrics
    cashflows = [-down_payment] + [cashflow] * loan_term
    internal_rate_of_return = npf.irr(cashflows) * 100
    net_present_value = npf.npv(risk_premium, [cashflow] * loan_term) - down_payment
    break_even_years = down_payment / cashflow if cashflow > 0 else None

    # Additional Metrics
    after_tax_cashflow = cashflow * (1 - 0.2)  # Assuming 20% tax
    real_cap_rate = cap_rate - inflation_rate
    real_npv = net_present_value / ((1 + inflation_rate / 100) ** loan_term)
    real_irr = internal_rate_of_return - inflation_rate
    renovation_roi = appreciation_rate * 100  # Simplified assumption
    liquidity_score = 1 / gross_rent_multiplier  # Proxy for liquidity
    holding_costs = total_expenses / 12
    brrrr_recycle_ratio = (loan_amount / purchase_price) * 100

    # New Financial Indicators
    equity_multiple = (cashflow * loan_term) / down_payment
    principal_reduction = loan_amount * (
        1 - (1 + monthly_interest_rate) ** -num_payments
    )
    loan_paydown_return = principal_reduction / down_payment
    interest_expense = loan_amount * (interest_rate / 100)
    interest_coverage_ratio = net_operating_income / interest_expense
    stressed_interest_rate = interest_rate + interest_rate_shock
    stressed_monthly_payment = (loan_amount * (stressed_interest_rate / 100 / 12)) / (
        1 - (1 + (stressed_interest_rate / 100 / 12)) ** -num_payments
    )
    stressed_dscr = net_operating_income / (stressed_monthly_payment * 12)
    break_even_rent = total_expenses / 12
    cagr = ((purchase_price * (1 + appreciation_rate) ** 5) / purchase_price) ** (
        1 / 5
    ) - 1
    market_volatility_index = market_volatility

    return {
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "mortgage_payment": mortgage_payment,
        "loan_to_value_ratio": (loan_amount / purchase_price) * 100,
        "debt_service_coverage_ratio": net_operating_income / annual_mortgage_payment,
        "annual_rent": annual_rent,
        "rental_yield": rental_yield,
        "gross_rent_multiplier": gross_rent_multiplier,
        "price_to_rent_ratio": price_to_rent_ratio,
        "net_operating_income": net_operating_income,
        "cashflow": cashflow,
        "cap_rate": cap_rate,
        "cash_on_cash_return": cash_on_cash_return,
        "internal_rate_of_return": internal_rate_of_return,
        "net_present_value": net_present_value,
        "break_even_years": break_even_years,
        "after_tax_cashflow": after_tax_cashflow,
        "real_cap_rate": real_cap_rate,
        "real_npv": real_npv,
        "real_irr": real_irr,
        "renovation_roi": renovation_roi,
        "liquidity_score": liquidity_score,
        "holding_costs": holding_costs,
        "brrrr_recycle_ratio": brrrr_recycle_ratio,
        "equity_multiple": equity_multiple,
        "loan_paydown_return": loan_paydown_return,
        "interest_coverage_ratio": interest_coverage_ratio,
        "stressed_dscr": stressed_dscr,
        "break_even_rent": break_even_rent,
        "compounded_annual_growth_rate": cagr,
        "market_volatility_index": market_volatility_index,
    }


# Example Usage
if __name__ == "__main__":
    financials = calculate_financials(
        purchase_price=1000000,
        down_payment_pr=0.20,
        loan_term=25,
        interest_rate=7,
        monthly_rent=5000,
        vacancy_rate=0.05,
        property_tax=5000,
        insurance_cost=1000,
        maintenance_cost=2000,
        management_fees=0.10,
        inflation_rate=4,
        risk_premium=0.05,
        appreciation_rate=0.03,
    )
    print(financials)
