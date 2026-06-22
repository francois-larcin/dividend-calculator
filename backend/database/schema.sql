-- Active: 1776718233368@@localhost@5432@dividend_db
--                                                DIVIDEND CALCULATOR _ DATABASE SCHEMA

DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS dividend_payments CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS stocks CASCADE;


--Table 1 : stocks
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY, 
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'JPY', 'HKD', 'TWD', 'NOK', 'CAD', 'DKK', 'GBP', 'AUD', 'SGD', 'CHF', 'PLN' )),
    last_update_at TIMESTAMP DEFAULT NOW()
);


-- Table 2 : users 
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
); 

-- Table 3 : portfolios
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('EUR', 'USD', 'JPY', 'HKD', 'TWD', 'NOK', 'CAD', 'DKK', 'GBP', 'AUD', 'SGD', 'CHF', 'PLN' )),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table 4 : dividend_payments
CREATE TABLE dividend_payments (
    id SERIAL PRIMARY KEY, 
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_id INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    amount_per_share DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL CHECK (total_amount > 0), 
    paid_at DATE DEFAULT CURRENT_DATE,
    ex_dividend_date DATE DEFAULT CURRENT_DATE
);

-- Table 5 : transactions
ALTER TABLE transactions 
ADD COLUMN avg_price_at_sell DECIMAL(10, 2) 
CHECK (avg_price_at_sell IS NULL OR avg_price_at_sell > 0)

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    stock_id INTEGER NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    "type" VARCHAR(4) NOT NULL CHECK (type IN ('BUY', 'SELL')),
    quantity DECIMAL(10, 2) NOT NULL CHECK (quantity > 0),
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    fee DECIMAL(10, 2) NOT NULL CHECK (fee >= 0),
    transaction_date TIMESTAMP DEFAULT NOW()
);


-- Index
CREATE INDEX idx_portfolio_user ON portfolios(user_id);
CREATE INDEX idx_transaction_portfolio ON transactions(portfolio_id);
CREATE INDEX idx_transaction_stock ON transactions(stock_id);
CREATE INDEX idx_div_payments_portfolio ON dividend_payments(portfolio_id);
CREATE INDEX idx_div_payments_stock ON dividend_payments(stock_id);



-- ==========================================
-- VUE : current_holdings
-- ==========================================

-- Calculates current portfolio stocks from transactions
DROP VIEW current_holdings

CREATE OR REPLACE VIEW current_holdings AS
SELECT
    t.portfolio_id,
    t.stock_id,
    s.ticker,
    s.company_name,
    s.currency,
    ROUND(
    SUM(CASE
        WHEN t.type = 'BUY' THEN t.quantity
        WHEN t.type = 'SELL' THEN -t.quantity
        END), 
        2) AS total_shares,

    ROUND(
        SUM(CASE WHEN t.type = 'BUY' THEN (t.quantity * t.price) + t.fee ELSE 0 END)
    /
    NULLIF(SUM(CASE WHEN t.type = 'BUY' THEN t.quantity ELSE 0 END), 0), 
        2) 
    AS avg_price,

    MIN(CASE WHEN t.type = 'BUY' THEN t.transaction_date END) AS date_added

FROM transactions t
JOIN stocks s ON s.id = t.stock_id
GROUP BY t.portfolio_id, t.stock_id, s.ticker, s.company_name, s.currency
HAVING SUM(CASE 
    WHEN t.type = 'BUY' THEN t.quantity  
    WHEN t.type = 'SELL' THEN -t.quantity
END) > 0
ORDER BY s.ticker;


-- ==========================================
-- PERMISSIONS
-- ==========================================

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO dividend_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dividend_user;









