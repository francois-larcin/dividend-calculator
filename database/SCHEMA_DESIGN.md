### Relationships
- **One user** can have **multiple portfolios** (1:N)
- **One portfolio** belongs to **one user** (N:1)
- **One portfolio** can contain **multiple holdings** (1:N)
- **One holding** belongs to **one portfolio** (N:1)

## Tables

### Table: `users`
Stores user authentication and profile information.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Auto-incrementing unique identifier
- `username` (VARCHAR(50) UNIQUE NOT NULL): User login name
- `email` (VARCHAR(100) UNIQUE NOT NULL): User email address
- `password_hash` (VARCHAR(255) NOT NULL): Bcrypt hashed password
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Account creation date

**Design decisions:**
- UNIQUE constraints on username and email prevent duplicates
- password_hash stores hashed passwords (never plain text)
- SERIAL for id ensures automatic incrementation

---

### Table: `portfolios`
Represents a collection of stocks owned by a user.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique portfolio identifier
- `user_id` (INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE): Owner
- `name` (VARCHAR(100) NOT NULL): Portfolio name (e.g., "Dividend Growth")
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Creation date

**Design decisions:**
- **Why separate portfolios from users?**
  - Allows users to organize stocks by strategy (growth, dividend, retirement)
  - Easier to calculate metrics per portfolio
  - Flexible: user can create unlimited portfolios

- **ON DELETE CASCADE:**
  - When a user is deleted, all their portfolios are automatically removed
  - Prevents orphaned data
  - Maintains referential integrity

---

### Table: `holdings`
Represents individual stock positions within a portfolio.

**Columns:**
- `id` (SERIAL PRIMARY KEY): Unique holding identifier
- `portfolio_id` (INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE): Parent portfolio
- `ticker` (VARCHAR(10) NOT NULL): Stock symbol (e.g., "AAPL", "MSFT")
- `company_name` (VARCHAR(255)): Company name (fetched from yfinance)
- `shares` (DECIMAL(10,2) NOT NULL CHECK > 0): Number of shares owned
- `avg_price` (DECIMAL(10,2) CHECK > 0): Average purchase price per share
- `date_added` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): When added to portfolio

**Design decisions:**
- **Why NOT UNIQUE on ticker?**
  - Same stock can appear in multiple portfolios
  - User might sell and rebuy the same stock
  - Example: AAPL in both "Growth" and "Dividend" portfolios

- **DECIMAL(10,2) for shares:**
  - Supports fractional shares (e.g., 10.50 shares)
  - Common with modern brokers (Robinhood, etc.)

- **CHECK constraints:**
  - shares > 0 prevents negative or zero positions
  - avg_price > 0 prevents data entry errors

- **company_name nullable:**
  - Fetched dynamically from yfinance API
  - Not critical for calculations
  - Reduces redundant storage

---

## Indexes

### Why these specific indexes?

```sql
CREATE INDEX idx_portfolios_user ON portfolios(user_id);
CREATE INDEX idx_holdings_portfolio ON holdings(portfolio_id);
```

**`idx_portfolios_user`:**
- **Most common query:** "Get all portfolios for user X"
- Without index: O(n) table scan
- With index: O(log n) lookup
- Used in: Dashboard, portfolio list, authentication flows

**`idx_holdings_portfolio`:**
- **Most common query:** "Get all stocks in portfolio X"
- Critical for JOIN operations
- Used in: Portfolio view, dividend calculations, projections

**Why NOT index ticker?**
- Ticker searches are rare in this app
- We filter by portfolio_id first, then ticker
- Composite index would be overkill for current use case

---

## Data Not Stored (and why)

### Dividend data
**Decision:** NOT stored in database

**Rationale:**
- Dividends change quarterly → frequent updates required
- yfinance API provides real-time data
- Avoids stale data issues
- Reduces storage and maintenance

**Tradeoff:**
- Slower queries (API calls required)
- Acceptable for this use case (small portfolios, infrequent access)

### Stock prices
**Decision:** Only average_buy_price stored, not current_price

**Rationale:**
- Current prices fetched from yfinance in real-time
- Historical prices not needed for dividend calculations
- avg_price sufficient for gain/loss calculations

---

## Complex Queries

#TODO#

## Schema Evolution Considerations

### Future additions (if time permits):
1. **Transactions table:** Track buy/sell history
2. **Dividend cache table:** Store fetched dividend data temporarily
3. **User preferences table:** Store settings (currency, notifications)

### Migration strategy:
- Use `ALTER TABLE` for schema changes
- Never DROP in production (use migrations)
- Always backup before schema changes

---

## Performance Considerations

**Current scale:** Optimized for:
- <100 users
- <50 portfolios per user
- <200 holdings per portfolio

**Bottleneck analysis:**
- Database queries: Fast (indexed)
- yfinance API calls: Slow (2-3s per ticker)
- Solution: Implement caching if needed

---

## Security Considerations

- **Password storage:** Bcrypt hashing (never plain text)
- **SQL injection:** Parameterized queries (psycopg2 handles this)
- **Access control:** user_id filtering on all queries
- **Cascade deletes:** Automatic cleanup prevents orphaned data

---

## Known Limitations

### Limitation: No transaction history
**Current implementation:**
- Each holding is stored as a single row with aggregated data
- `avg_price` is updated when buying/selling more shares
- Transaction history is lost

**Impact:**
- Cannot track when specific purchases were made
- Cannot generate detailed transaction reports
- PRU recalculated on each purchase (formula implemented in app code)

**Justification:**
- Simpler implementation for MVP
- Sufficient for basic dividend tracking
- Acceptable tradeoff for a 1-month project timeline

**Future improvement:**
Add a `transactions` table to track individual buy/sell operations:
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER,
    ticker VARCHAR(10),
    type VARCHAR(4) CHECK (type IN ('BUY', 'SELL')),
    shares DECIMAL(10,2),
    price DECIMAL(10,2),
    date TIMESTAMP
);
```
Then calculate current holdings dynamically from transaction history.