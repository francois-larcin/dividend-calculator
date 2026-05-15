"""
Tests for TransactionService

Tests cover:
- CRUD operations
- buy_stock() orchestration (with/without yfinance)
- sell_stock() with validations
- Edge cases and error handling
"""

import pytest
import datetime as dt
from backend.services.transaction_service import TransactionService
from backend.repositories import (
    TransactionRepository,
    StockRepository,
    HoldingRepository,
    PortfolioRepository
)
from backend.models import TransactionData, StockData, PortfolioData


# ==========================================
# CONFIGURATION
# ==========================================

db_config = {
    'host': 'localhost',
    'database': 'dividend_db',
    'user': 'dividend_user',
    'password': 'dividend123'
}


# ==========================================
# FIXTURES
# ==========================================

@pytest.fixture
def repositories():
    """Create all repository instances."""
    return {
        'transaction_repo': TransactionRepository(db_config),
        'stock_repo': StockRepository(db_config),
        'holding_repo': HoldingRepository(db_config),
        'portfolio_repo': PortfolioRepository(db_config)
    }


@pytest.fixture
def service(repositories):
    """Create TransactionService with injected repositories."""
    return TransactionService(
        transaction_repo=repositories['transaction_repo'],
        stock_repo=repositories['stock_repo'],
        holding_repo=repositories['holding_repo'],
        portfolio_repo=repositories['portfolio_repo']
    )


@pytest.fixture
def test_portfolio(repositories):
    """
    Create a test portfolio and clean up after test.
    
    Yields:
        portfolio_id: ID of the created test portfolio
    """
    portfolio = PortfolioData(
        user_id=1,
        name="Test Portfolio",
        currency="USD",
        id=194
    )
    portfolio_id = repositories['portfolio_repo'].add(portfolio)
    
    #Verify it was created
    created = repositories['portfolio_repo'].get_by_id(portfolio_id)
    assert created is not None, f"Failed to create test portfolio {portfolio_id}"
    
    yield portfolio_id
    
    # Cleanup: Delete all transactions first (FK constraint)
    try:
        transactions = repositories['transaction_repo'].get_by_portfolio(portfolio_id)
        for transaction in transactions:
            repositories['transaction_repo'].delete(transaction.id)
    except:
        pass
    
    # Then delete portfolio
    try:
        repositories['portfolio_repo'].delete(portfolio_id)
    except:
        pass


@pytest.fixture
def test_stock(repositories):
    """
    Create test stock and cleanup after.
    Cleanup transactions first to avoid FK constraint errors.
    """
    # Create stock
    stock = StockData(
        ticker="TESTSTOCK",
        company_name="Test Company Inc.",
        sector="Technology",
        industry="Software",
        currency="USD"
    )
    stock_id = repositories['stock_repo'].add(stock)
    
    # Verify it was created
    created = repositories['stock_repo'].get_by_id(stock_id)
    assert created is not None, f"Failed to create test stock {stock_id}"
    
    yield stock_id
    
    # Cleanup: Delete all transactions first (FK constraint)
    try:
        transactions = repositories['transaction_repo'].get_by_stock(stock_id)
        for transaction in transactions:
            repositories['transaction_repo'].delete(transaction.id)
    except:
        pass
    
    # Then delete stock
    try:
        repositories['stock_repo'].delete(stock_id)
    except:
        pass


# ==========================================
# TESTS - QUERIES
# ==========================================

def test_get_portfolio_transactions(service, test_portfolio, test_stock):
    """Test getting all transactions for a portfolio."""
    # Create a transaction
    transaction = TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock,
        type='BUY',
        quantity=10,
        price=100.0,
        fee=1.0
    )
    transaction_id = service.create_transaction(transaction)
    
    # Get portfolio transactions
    transactions = service.get_portfolio_transactions(test_portfolio)
    
    assert len(transactions) > 0
    assert any(t.id == transaction_id for t in transactions)
    
    # Cleanup
    service.transaction_repo.delete(transaction_id)


def test_get_stock_transactions(service, test_portfolio, test_stock):
    """Test getting all transactions for a stock."""
    # Create a transaction
    transaction = TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock,
        type='BUY',
        quantity=5,
        price=50.0
    )
    transaction_id = service.create_transaction(transaction)
    
    # Get stock transactions
    transactions = service.get_stock_transactions(test_stock)
    
    assert len(transactions) > 0
    assert any(t.stock_id == test_stock for t in transactions)
    
    # Cleanup
    service.transaction_repo.delete(transaction_id)


# ==========================================
# TESTS - BUY STOCK
# ==========================================

def test_buy_stock_existing_stock(service, test_portfolio, test_stock, repositories):
    """Test buying a stock that already exists in database."""
    # Get stock ticker
    stock = repositories['stock_repo'].get_by_id(test_stock)
    
    # Buy stock
    transaction_id = service.buy_stock(
        portfolio_id=test_portfolio,
        ticker=stock.ticker,
        quantity=10,
        price=100.50,
        fee=2.0
    )
    
    assert isinstance(transaction_id, int)
    
    # Verify transaction created
    transaction = service.get_transaction(transaction_id)
    assert transaction is not None
    assert transaction.portfolio_id == test_portfolio
    assert transaction.stock_id == test_stock
    assert transaction.type == 'BUY'
    assert transaction.quantity == 10
    assert transaction.price == 100.50
    assert transaction.fee == 2.0
    
    # Cleanup
    service.transaction_repo.delete(transaction_id)


def test_buy_stock_new_from_yfinance(service, test_portfolio, repositories):
    """
    Test buying a stock that doesn't exist in DB.
    Should fetch from yfinance and create stock.
    """
    ticker = "AAPL"  # Real stock on yfinance
    
    # Delete if exists (cleanup from previous test)
    existing = repositories['stock_repo'].get_by_ticker(ticker)
    if existing:
        repositories['stock_repo'].delete(existing.id)
    
    # Buy stock (should fetch from yfinance)
    transaction_id = service.buy_stock(
        portfolio_id=test_portfolio,
        ticker=ticker,
        quantity=5,
        price=150.0,
        fee=1.5
    )
    
    assert isinstance(transaction_id, int)
    
    # Verify stock was created
    stock = repositories['stock_repo'].get_by_ticker(ticker)
    assert stock is not None
    assert stock.ticker == ticker.upper()
    assert stock.company_name  # Should have fetched from yfinance
    
    # Verify transaction
    transaction = service.get_transaction(transaction_id)
    assert transaction.stock_id == stock.id
    
    # Cleanup
    service.transaction_repo.delete(transaction_id)
    repositories['stock_repo'].delete(stock.id)


def test_buy_stock_invalid_quantity(service, test_portfolio):
    """Test buying with invalid quantity raises ValueError."""
    with pytest.raises(ValueError, match="Quantity must be positive"):
        service.buy_stock(
            portfolio_id=test_portfolio,
            ticker="AAPL",
            quantity=0,  # Invalid
            price=100.0
        )
    
    with pytest.raises(ValueError, match="Quantity must be positive"):
        service.buy_stock(
            portfolio_id=test_portfolio,
            ticker="AAPL",
            quantity=-10,  # Invalid
            price=100.0
        )


def test_buy_stock_invalid_price(service, test_portfolio):
    """Test buying with invalid price raises ValueError."""
    with pytest.raises(ValueError, match="Price must be positive"):
        service.buy_stock(
            portfolio_id=test_portfolio,
            ticker="AAPL",
            quantity=10,
            price=0  # Invalid
        )
    
    with pytest.raises(ValueError, match="Price must be positive"):
        service.buy_stock(
            portfolio_id=test_portfolio,
            ticker="AAPL",
            quantity=10,
            price=-50.0  # Invalid
        )


def test_buy_stock_invalid_portfolio(service):
    """Test buying with non-existent portfolio raises ValueError."""
    with pytest.raises(ValueError, match="Portfolio .* not found"):
        service.buy_stock(
            portfolio_id=999999,  # Non-existent
            ticker="AAPL",
            quantity=10,
            price=100.0
        )


# ==========================================
# TESTS - SELL STOCK
# ==========================================

def test_sell_stock_success(service, test_portfolio, test_stock, repositories):
    """Test selling stock with sufficient quantity."""
    # Get stock ticker
    stock = repositories['stock_repo'].get_by_id(test_stock)
    
    # First, buy 20 shares
    buy_id = service.buy_stock(
        portfolio_id=test_portfolio,
        ticker=stock.ticker,
        quantity=20,
        price=100.0
    )
    
    # Then sell 10 shares
    sell_id = service.sell_stock(
        portfolio_id=test_portfolio,
        ticker=stock.ticker,
        quantity=10,
        price=110.0,
        fee=1.0
    )
    
    assert isinstance(sell_id, int)
    
    # Verify sell transaction
    transaction = service.get_transaction(sell_id)
    assert transaction.type == 'SELL'
    assert transaction.quantity == 10
    assert transaction.price == 110.0
    
    # Cleanup
    service.transaction_repo.delete(buy_id)
    service.transaction_repo.delete(sell_id)


def test_sell_stock_insufficient_quantity(service, test_portfolio, test_stock, repositories):
    """Test selling more shares than owned raises ValueError."""
    stock = repositories['stock_repo'].get_by_id(test_stock)
    
    # Buy 10 shares
    buy_id = service.buy_stock(
        portfolio_id=test_portfolio,
        ticker=stock.ticker,
        quantity=10,
        price=100.0
    )
    
    # Try to sell 20 shares (more than owned)
    with pytest.raises(ValueError, match="Insufficient shares"):
        service.sell_stock(
            portfolio_id=test_portfolio,
            ticker=stock.ticker,
            quantity=20,  # More than owned
            price=110.0
        )
    
    # Cleanup
    service.transaction_repo.delete(buy_id)


def test_sell_stock_no_holding(service, test_portfolio, test_stock, repositories):
    """Test selling stock with no holding raises ValueError."""
    stock = repositories['stock_repo'].get_by_id(test_stock)
    
    # Try to sell without owning any
    with pytest.raises(ValueError, match="No holding for"):
        service.sell_stock(
            portfolio_id=test_portfolio,
            ticker=stock.ticker,
            quantity=10,
            price=100.0
        )


def test_sell_stock_not_found(service, test_portfolio):
    """Test selling non-existent stock raises ValueError."""
    with pytest.raises(ValueError, match="Stock .* not found"):
        service.sell_stock(
            portfolio_id=test_portfolio,
            ticker="NONEXISTENT",
            quantity=10,
            price=100.0
        )


def test_sell_stock_invalid_quantity(service, test_portfolio):
    """Test selling with invalid quantity raises ValueError."""
    with pytest.raises(ValueError, match="Quantity must be positive"):
        service.sell_stock(
            portfolio_id=test_portfolio,
            ticker="AAPL",
            quantity=0,
            price=100.0
        )


# ==========================================
# TESTS - YFINANCE FETCH
# ==========================================

def test_fetch_invalid_ticker(service, test_portfolio):
    """Test fetching invalid ticker from yfinance raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        service.buy_stock(
            portfolio_id=test_portfolio,
            ticker="INVALIDTICKER123",  # Invalid ticker
            quantity=10,
            price=100.0
        )


# ==========================================
# RUN TESTS
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])