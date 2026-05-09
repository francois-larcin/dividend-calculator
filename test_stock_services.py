# test_portfolio_service.py (à la racine du projet)

from backend.services.portfolio_service import PortfolioService

from backend.repositories import (
    PortfolioRepository,
    HoldingRepository,
    TransactionRepository
)

# Config DB
db_config = {
    'host': 'localhost',
    'database': 'dividend_db',
    'user': 'dividend_user',
    'password': 'dividend123'
}

# Créer les repositories
portfolio_repo = PortfolioRepository(db_config)
holding_repo = HoldingRepository(db_config)
transaction_repo = TransactionRepository(db_config)

# Créer le service (DEPENDENCY INJECTION)
service = PortfolioService(
    portfolio_repo=portfolio_repo,
    holding_repo=holding_repo,
    transaction_repo=transaction_repo
)

# Tests
print("=== Test create_portfolio ===")
portfolio_id = service.create_portfolio(
    user_id=1,
    name="Mon Portfolio Dividendes",
    currency="EUR"
)
print(f"✅ Portfolio créé avec ID: {portfolio_id}")

print("\n=== Test get_portfolio ===")
portfolio = service.get_portfolio(portfolio_id)
print(f"✅ Portfolio récupéré: {portfolio.name}")

print("\n=== Test get_portfolio_with_holdings ===")
portfolio_with_holdings = service.get_portfolio_with_holdings(portfolio_id)
print(f"✅ Portfolio avec {len(portfolio_with_holdings.holdings)} holdings")