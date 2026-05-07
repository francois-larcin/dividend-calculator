# test_stock_repo.py (à la racine)

from backend.repositories.stock_repository import StockRepository
from backend.models import StockData
import datetime as dt

# Config DB
db_config = {
    'host': 'localhost',
    'database': 'dividend_db',
    'user': "dividend_user" ,
    'password': 'dividend123'
}

repo = StockRepository(db_config)

# Test add
print("=== Test add() ===")
new_stock = StockData(
    id=0,
    ticker='AAPL',
    company_name='Apple Inc.',
    sector='Technology',
    industry='Consumer Electronics',
    currency='USD',
    dividend_frequency=4
)

new_id = repo.add(new_stock)
print(f"✅ Stock créé avec ID: {new_id}")

# Test get_by_id
print("\n=== Test get_by_id() ===")
stock = repo.get_by_id(new_id)
print(f"✅ Stock récupéré: {stock}")

# Test get_by_ticker
print("\n=== Test get_by_ticker() ===")
stock = repo.get_by_ticker('AAPL')
print(f"✅ Stock trouvé: {stock}")

# Test get_all
print("\n=== Test get_all() ===")
all_stocks = repo.get_all()
print(f"✅ Nombre de stocks: {len(all_stocks)}")

# Test search_by_sector
print("\n=== Test search_by_sector() ===")
tech_stocks = repo.search_by_sector('Technology')
print(f"✅ Stocks Technology: {len(tech_stocks)}")