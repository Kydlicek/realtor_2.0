-- Create properties table (common and specific attributes for both flats and houses)
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    property_type VARCHAR(50) NOT NULL,
    size FLOAT NOT NULL,
    rooms INT NOT NULL,
    gps_lat FLOAT NOT NULL,
    gps_lon FLOAT NOT NULL,
    construction_year INT,
    last_reconstruction_year INT,
    energy_rating VARCHAR(50),
    has_balcony BOOLEAN DEFAULT FALSE,
    has_parking BOOLEAN DEFAULT FALSE,
    condition VARCHAR(50),
    floor INT,
    building_floors INT,
    elevator BOOLEAN DEFAULT FALSE,
    garden_size_m2 FLOAT,
    garage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create listings table (tracks all listings)
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    property_id INT REFERENCES properties(id) ON DELETE CASCADE,  -- Foreign key to properties
    source VARCHAR(255),
    external_id VARCHAR(255),
    url VARCHAR(255) UNIQUE NOT NULL,
    price FLOAT NOT NULL,
    rent BOOLEAN DEFAULT FALSE,
    contact VARCHAR(255),
    description TEXT,
    hash VARCHAR(255) NOT NULL,
    date_created TIMESTAMP,
    date_removed TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rent_price FLOAT,
    electricity_utilities FLOAT,
    provision_rk FLOAT,
    downpayment_1x FLOAT,
    downpayment_2x FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create financials table (for investment analysis)
CREATE TABLE financials (
    id SERIAL PRIMARY KEY,
    listing_id INT REFERENCES listings(id) ON DELETE CASCADE,  -- Foreign key to listings
    rental_yield FLOAT,  -- Annual rental yield as a percentage
    monthly_rent FLOAT,  -- Estimated monthly rent
    monthly_payment FLOAT,  -- Estimated monthly mortgage payment
    down_payment FLOAT,  -- Required down payment
    appreciation_rate FLOAT,  -- Annual price appreciation rate
    property_tax FLOAT,  -- Annual property tax
    insurance_cost FLOAT,  -- Annual insurance cost
    maintenance_cost FLOAT,  -- Annual maintenance cost
    management_fees FLOAT,  -- Annual property management fees
    net_operating_income FLOAT,  -- NOI: (Monthly Rent * 12) - Operating Expenses
    cashflow FLOAT,  -- NOI - Mortgage Payments
    cash_on_cash_return FLOAT,  -- (Annual Cashflow / Total Cash Invested) * 100
    loan_to_value_ratio FLOAT,  -- (Loan Amount / Property Value) * 100
    debt_service_coverage_ratio FLOAT,  -- NOI / Annual Mortgage Payments
    price_to_rent_ratio FLOAT,  -- Property Price / Annual Rent
    gross_rent_multiplier FLOAT,  -- Property Price / Annual Rent
    capitalization_rate FLOAT,  -- (NOI / Property Price) * 100
    internal_rate_of_return FLOAT,  -- Annualized return over holding period
    net_present_value FLOAT,  -- Present value of future cashflows
    break_even_years FLOAT,  -- Years to recoup initial investment
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster queries
CREATE INDEX idx_properties_location ON properties (gps_lat, gps_lon);
CREATE INDEX idx_properties_type ON properties (property_type);
CREATE INDEX idx_listings_price ON listings (price);
CREATE INDEX idx_listings_rent ON listings (rent);
CREATE INDEX idx_listings_active ON listings (is_active);
CREATE INDEX idx_financials_yield ON financials (rental_yield);