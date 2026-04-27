-- ==========================================
-- TEST DATA for Development
-- ==========================================
-- Purpose: Realistic sample data to test queries and features
-- Usage: psql -h localhost -U dividend_user -d dividend_db -f database/test_data.sql

-- Clean existing test data

DELETE FROM transactions;
DELETE FROM holdings;
DELETE FROM portfolios WHERE id > 1;
DELETE FROM users WHERE id > 1;
DELETE FROM stocks;


-- Reset sequences
ALTER SEQUENCE transactions_id_seq RESTART WITH 1;
ALTER SEQUENCE holdings_id_seq RESTART WITH 1;
ALTER SEQUENCE users_id_seq RESTART WITH 2;
ALTER SEQUENCE portfolios_id_seq RESTART WITH 2;


-- ====================================================
-- STOCKS 
-- ====================================================

INSERT INTO stocks (ticker, company_name) VALUES
('AAPL', 'Apple Inc.'),
('MSFT', 'Microsoft Corporation'),
('JNJ', 'Johnson & Johnson'),
('KO', 'The Coca-Cola Company'),
('PEP', 'PepsiCo Inc.'),
('O', 'Realty Income Corporation'),
('VZ', 'Verizon Communications Inc.');

-- ====================================================
--USERS 
-- ====================================================

INSERT INTO users (username, email, password_hash) 
VALUES ('investor_bob', 'bob@invest.com', 'hash_456');

-- ====================================================
--PORTFOLIOS 
-- ====================================================

-- testuser (id=1) portfolios
INSERT INTO portfolios (user_id, name) VALUES 
(1, 'Dividendes Mensuels'),
(1, 'Croissance Long Terme');

-- investor_bob (id=2) portfolio
INSERT INTO portfolios (user_id, name) VALUES 
(2, 'Portfolio Retraite');

-- ====================================================
--HOLDINGS 
-- ====================================================

-- Portfolio "Mon portefeuille test" (id=1)
INSERT INTO holdings (portfolio_id, ticker, total_shares, avg_price) VALUES
(1, 'AAPL', 40.00, 150.00),
(1, 'MSFT', 50.00, 300.00),
(1, 'JNJ', 8.00, 160.00);

-- Portfolio "Dividendes Mensuels" (id=2)
INSERT INTO holdings (portfolio_id, ticker, total_shares, avg_price) VALUES
(2, 'KO', 20.00, 55.00),
(2, 'PEP', 15.00, 170.00),
(2, 'O', 30.00, 62.00);

-- Portfolio "Croissance Long Terme" (id=3) - INTENTIONALLY EMPTY
-- This tests LEFT JOIN and COALESCE in queries

-- Portfolio "Portfolio Retraite" (id=4)
INSERT INTO holdings (portfolio_id, ticker, total_shares, avg_price) VALUES
(4, 'AAPL', 25.00, 145.00),
(4, 'VZ', 40.00, 38.00);

-- ====================================================
-- TRANSACTIONS (optionnel - pour tester l'historique)
-- ====================================================

-- Exemple : Historique des achats qui ont mené aux holdings ci-dessus
INSERT INTO transactions (portfolio_id, ticker, "type", quantity, price, transaction_date) VALUES
-- Portfolio 1 - AAPL (total: 10 actions)
(1, 'AAPL', 'BUY', 10.00, 150.00, '2024-01-15 10:30:00'),

-- Portfolio 1 - MSFT (total: 5 actions)
(1, 'MSFT', 'BUY', 5.00, 300.00, '2024-02-10 14:20:00'),

-- Portfolio 2 - KO (total: 20 actions, achetées en 2 fois)
(2, 'KO', 'BUY', 15.00, 54.00, '2024-01-20 09:15:00'),
(2, 'KO', 'BUY', 5.00, 58.00, '2024-03-05 11:45:00');