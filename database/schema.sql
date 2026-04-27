--                                                DIVIDEND CALCULATOR _ DATABASE SCHEMA

DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS holdings CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS stocks CASCADE;


--Table 1 : stocks
CREATE TABLE stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 4 : holdings
CREATE TABLE holdings (
    id SERIAL PRIMARY KEY, 
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL REFERENCES stocks(ticker), 
    total_shares DECIMAL(10, 2) NOT NULL CHECK (total_shares > 0), 
    avg_price DECIMAL(10, 2) NOT NULL CHECK (avg_price > 0), 
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 5 : transactions
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL REFERENCES stocks(ticker),
    "type" VARCHAR(4) NOT NULL CHECK (type IN ('BUY', 'SELL')),
    quantity DECIMAL(10, 2) NOT NULL CHECK (quantity > 0),
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    transaction_date TIMESTAMP DEFAULT NOW()
);


-- Index
CREATE INDEX idx_portfolio_user ON portfolios(user_id);
CREATE INDEX idx_holding_portfolio ON holdings(portfolio_id);


-- Test data
INSERT INTO stocks (ticker, company_name) VALUES
('AAPL', 'Apple Inc.'),
('MSFT', 'Microsoft Corporation'),
('JNJ', 'Johnson & Johnson'),
('KO', 'The Coca-Cola Company');

INSERT INTO users (username, email, password_hash)
VALUES ('testuser', 'test@test.com', 'temporary_hash_123');

INSERT INTO portfolios (user_id, name)
VALUES (1, 'My dividend oriented portfolio');