--                                                DIVIDEND CALCULATOR _ DATABASE SCHEMA

DROP TABLE IF EXISTS holdings CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Table 1 : Users 
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 

-- Table 2 : Portfolios
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3 : Holdings

CREATE TABLE holdings (
    id SERIAL PRIMARY KEY, 
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    ticker VARCHAR(50) NOT NULL, 
    company_name VARCHAR(200),
    shares DECIMAL(10, 2) NOT NULL, 
    avg_price DECIMAL(10, 2) NOT NULL, 
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Index
CREATE INDEX idx_portfolio_user ON portfolios(user_id);
CREATE INDEX idx_holding_portfolio ON holdings(portfolio_id);

-- Test data
INSERT INTO users (username, email, password_hash)
VALUES ('testuser', 'test@test.com', 'temporary_hash_123');

INSERT INTO portfolios (user_id, name)
VALUES (1, 'My dividend oriented portfolio');