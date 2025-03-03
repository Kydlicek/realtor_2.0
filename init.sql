-- Create properties table (common and specific attributes for both flats and houses)
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    property_type VARCHAR(50) NOT NULL,
    -- common attributes
    size_m2 FLOAT NOT NULL,
    rooms INT NOT NULL,
    -- if true + kk, if false + 1
    has_separate_kitchen BOOLEAN DEFAULT FALSE,
    -- location attributes 
    gps_lat FLOAT NOT NULL,
    gps_lon FLOAT NOT NULL,
    country VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    city_district VARCHAR(50),
    address VARCHAR(255) NOT NULL,
    -- age attributes
    year_built INT,
    last_reconstruction_year INT,
    condition ENUM('new','after renovation' 'good', 'needs renovation', 'ruin') DEFAULT 'good'
    -- property specific
    has_balcony BOOLEAN DEFAULT FALSE,
    balcony_size_m2 FLOAT DEFAULT 0,
    has_terrace BOOLEAN DEFAULT FALSE,
    terrace_size_m2 INT DEFAULT 0,
    has_garden BOOLEAN DEFAULT FALSE,
    garden_size_m2 INT DEFAULT 0,
    has_parking BOOLEAN DEFAULT FALSE,
    parking INT DEFAULT 0,
    has_garage BOOLEAN DEFAULT FALSE,
    garage INT DEFAULT 0,
    has_cellar BOOLEAN DEFAULT FALSE,
    cellar_size_m2 INT DEFAULT 0,
    is_furnished BOOLEAN DEFAULT FALSE,
    has_lift BOOLEAN DEFAULT FALSE,

    -- house specific
    -- in case of flat is how many floor does apartment has in case of building it's how many floor it has
    building_floors INT,
    flat_floor INT,
    energy_rating ENUM('A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G') DEFAULT 'C'

    -- 
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create listings table (tracks all listings)
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,  -- Foreign key to properties
    source VARCHAR(255),  -- Where the listing was scraped from
    listing_url VARCHAR(255) UNIQUE NOT NULL,  -- Avoid duplicates
    api_url VARCHAR(255),  -- API endpoint for the listing
    description TEXT,

    -- Pricing Details
    price FLOAT NOT NULL,  -- Sale price
    rent_price FLOAT DEFAULT NULL,  -- Rent price (only for rentals)
    building_fees FLOAT DEFAULT 0,  -- Additional fees for trash, maintenance, etc.
    electricity_utilities FLOAT DEFAULT 0,  -- Monthly electricity/utilities
    provision_rk FLOAT DEFAULT 0,  -- Commission for the real estate agency
    currency ENUM('EUR', 'USD', 'CZK', 'GBP') NOT NULL DEFAULT 'CZK',  -- Currency type

    -- Contact Information (Stored as JSON)
    contact JSONB,

    -- Listing Status
    listing_status ENUM('active', 'expired', 'sold', 'rented', 'removed') DEFAULT 'active',

    -- Timestamps
    listed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- When it was first listed
    date_removed TIMESTAMP,  -- When the listing was removed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- Track Price Changes (for both sales & rentals)
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,  -- Link to the property
    listing_id INT REFERENCES listings(id) ON DELETE CASCADE,
    price NUMERIC(12,2) NOT NULL,  -- The recorded price at that time
    price_type ENUM('sale', 'rent') NOT NULL,  -- Distinguish sale vs. rental price
    currency ENUM('EUR', 'USD', 'CZK', 'GBP') NOT NULL DEFAULT 'CZK',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When this price was recorded
);

CREATE TABLE macro_economic_data (
    id SERIAL PRIMARY KEY,
    interest_rate NUMERIC(5,2),  -- Mortgage interest rate
    inflation_rate NUMERIC(5,2),  -- General inflation
    vacancy_rate NUMERIC(5,2), --Rate at wich rents are empty
    risk_premium NUMERIC(5,2),  -- Risk factor for NPV calculations
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-- Financials Table for Real Estate Investment Analysis
CREATE TABLE financials (
    id SERIAL PRIMARY KEY,
    listing_id INT REFERENCES listings(id) ON DELETE CASCADE,  -- Link to property listing

        -- 🏦 Core Loan Parameters
    purchase_price NUMERIC(12,2),  -- Property purchase price
    down_payment_pr NUMERIC(6,4),  -- Down payment percentage (20% = 0.20)
    loan_term INT,  -- Loan duration in years
    interest_rate NUMERIC(6,4),  -- Annual interest rate (7% = 0.07)

    -- 🏠 Mortgage Calculations (Could be calculated fields)
    loan_amount NUMERIC(12,2),  -- purchase_price * (1 - down_payment_pr)
    mortgage_payment NUMERIC(12,2),  -- Monthly payment (PMT calculation)
    loan_to_value_ratio NUMERIC(6,2),  -- (loan_amount / purchase_price) * 100

    -- 📊 Rental Income Basics
    monthly_rent NUMERIC(12,2),  -- Base monthly rental income
    vacancy_rate NUMERIC(6,4),  -- Vacancy allowance (5% = 0.05)
    management_fee_rate NUMERIC(6,4),  -- Management fee percentage (10% = 0.10)

    -- 🌐 Economic Assumptions
    inflation_rate NUMERIC(6,4),  -- Annual inflation assumption
    risk_premium NUMERIC(6,4),  -- Risk premium for discount rates
    appreciation_rate NUMERIC(6,4),  -- Expected annual appreciation

    -- 🏠 Mortgage & Loan Metrics
    down_payment NUMERIC(12,2),  -- Initial cash investment
    loan_to_value_ratio NUMERIC(6,2),  -- (Loan Amount / Property Price) * 100
    debt_service_coverage_ratio NUMERIC(6,2),  -- NOI / Annual Mortgage Payment
    loan_paydown_return NUMERIC(6,2),  -- Return from paying down loan principal
    interest_coverage_ratio NUMERIC(6,2),   -- EBITDA / Interest Expense
    stressed_dscr NUMERIC(6,2),  -- DSCR under stressed conditions


    -- 💰 Rental & Income Metrics
    annual_rent NUMERIC(12,2),  -- Monthly rent * 12
    rental_yield NUMERIC(6,2),  -- (Annual Rent / Purchase Price) * 100
    gross_rent_multiplier NUMERIC(6,2),  -- Property Price / Annual Rent
    price_to_rent_ratio NUMERIC(6,2),  -- Purchase Price / Annual Rent
    break_even_rent NUMERIC(12,2),  -- Minimum rent needed to break even

    -- 📈 Profitability Metrics
    net_operating_income NUMERIC(12,2),  -- NOI: Rent - Operating Expenses
    cashflow NUMERIC(12,2),  -- NOI - Mortgage Payments
    cap_rate NUMERIC(6,2),  -- (NOI / Property Price) * 100
    cash_on_cash_return NUMERIC(6,2),  -- (Annual Cashflow / Down Payment) * 100
    equity_multiple NUMERIC(6,2),  -- Total Cashflow / Equity Invested

    -- 📊 Risk & Return Metrics
    compounded_annual_growth_rate NUMERIC(6,2),  -- CAGR over holding period
    internal_rate_of_return NUMERIC(6,2),  -- Estimated IRR over holding period
    net_present_value NUMERIC(12,2),  -- Discounted future cashflows
    break_even_years NUMERIC(6,2),  -- Years to recoup initial investment

    -- 💸 Expense Metrics
    property_tax NUMERIC(12,2),  -- Annual property tax
    insurance_cost NUMERIC(12,2),  -- Annual insurance cost
    maintenance_cost NUMERIC(12,2),  -- Annual maintenance cost
    management_fees NUMERIC(12,2),  -- Annual property management fees
    operating_expenses NUMERIC(12,2),  -- Sum of all expenses

    -- 📌 Additional Investment Metrics
    
    after_tax_cashflow NUMERIC(12,2),  -- Cashflow after estimated taxes
    real_cap_rate NUMERIC(6,2),  -- Inflation-adjusted Cap Rate
    real_npv NUMERIC(12,2),  -- Inflation-adjusted Net Present Value
    real_irr NUMERIC(6,2),  -- Inflation-adjusted Internal Rate of Return
    renovation_roi NUMERIC(6,2),  -- Expected return on renovations
    time_on_market INT,  -- Number of days property has been listed
    liquidity_score NUMERIC(6,2),  -- Estimate of how easy it is to sell
    holding_costs NUMERIC(12,2),  -- Costs when property is vacant
    brrrr_recycle_ratio NUMERIC(6,2),  -- % of cash recovered in BRRRR strategy

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

);
