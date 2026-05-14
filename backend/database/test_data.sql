
-- ==========================================
-- TEST DATA for Development
-- ==========================================

-- Clean existing test data
DELETE FROM transactions;
DELETE FROM dividend_payments;
DELETE FROM portfolios;
DELETE FROM users;
DELETE FROM stocks;

-- Reset sequences
ALTER SEQUENCE transactions_id_seq RESTART WITH 1;
ALTER SEQUENCE dividend_payments_id_seq RESTART WITH 1;
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE portfolios_id_seq RESTART WITH 1;
ALTER SEQUENCE stocks_id_seq RESTART WITH 1;

-- ====================================================
-- STOCKS
-- ====================================================

INSERT INTO stocks (ticker, company_name, currency, sector, industry) VALUES
('AAPL','Apple Inc.', 'USD', 'Technology', 'Consumer Electronics'),
('MSFT','Microsoft Corporation','USD', 'Technology','Software'),
('JNJ','Johnson & Johnson','USD', 'Healthcare','Pharmaceuticals'),
('KO','The Coca-Cola Company','USD', 'Consumer Staples',  'Beverages'),
('PEP','PepsiCo Inc.','USD', 'Consumer Staples',  'Beverages'),
('O', 'Realty Income Corporation','USD', 'Real Estate','REIT'),
('VISTA', 'Vista Energy','USD','Energy', 'Oil & Gas'),
('ASML','ASML Holding','EUR', 'Technology','Semiconductors'),
('NOVO', 'Novo Nordisk', 'DKK', 'Healthcare', 'Pharmaceuticals'),
('SHEL', 'Shell PLC','GBP', 'Energy', 'Oil & Gas');

-- ====================================================
-- USERS
-- ====================================================

INSERT INTO users (username, email, password_hash)
VALUES
('testuser',     'test@test.com',   'temporary_hash_123'),
('investor_bob', 'bob@invest.com',  'hash_456');

-- ====================================================
-- PORTFOLIOS
-- ====================================================

-- testuser (id=1)
INSERT INTO portfolios (user_id, name, currency) VALUES
(1, 'Dividendes Mensuels',    'EUR'),
(1, 'Croissance Long Terme',  'USD');

-- investor_bob (id=2)
INSERT INTO portfolios (user_id, name, currency) VALUES
(2, 'Portfolio Retraite',     'GBP');

-- ====================================================
-- TRANSACTIONS
-- ====================================================

INSERT INTO transactions (portfolio_id, stock_id, type, quantity, price, fee, transaction_date) VALUES
-- Portfolio 1 — Dividendes Mensuels
(1, 1,  'BUY', 10.00, 150.00, 1.50, '2024-01-15 10:30:00'),
(1, 4,  'BUY', 15.00,  54.00, 1.00, '2024-01-20 09:15:00'),
(1, 4,  'BUY',  5.00,  58.00, 1.00, '2024-03-05 11:45:00'),
(1, 6,  'BUY', 30.00,  62.00, 0.00, '2024-02-01 08:00:00'),

-- Portfolio 2 — Croissance Long Terme
(2, 2,  'BUY',  5.00, 300.00, 1.50, '2024-02-10 14:20:00'),
(2, 8,  'BUY',  8.00, 680.00, 2.00, '2024-03-12 10:00:00'),

-- Portfolio 3 — Portfolio Retraite (investor_bob)
(3, 1,  'BUY', 25.00, 145.00, 1.50, '2024-01-05 09:00:00'),
(3, 7,  'BUY', 40.00,  38.00, 1.00, '2024-01-10 11:00:00'),
(3, 10, 'BUY', 20.00, 2400.00, 3.00, '2024-02-20 15:30:00');

-- ====================================================
-- DIVIDEND PAYMENTS
-- ====================================================

INSERT INTO dividend_payments (portfolio_id, stock_id, amount_per_share, total_amount, ex_dividend_date, paid_at) VALUES
(1, 4,  0.46, 9.20,  '2024-02-09', '2024-03-01'),
(1, 6,  0.26, 7.80,  '2024-01-31', '2024-02-15'),
(2, 2,  0.75, 3.75,  '2024-02-14', '2024-03-14'),
(3, 7,  0.67, 26.80, '2024-02-09', '2024-03-01');
