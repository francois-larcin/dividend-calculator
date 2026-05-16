"""
Tests for HoldingService

Tests cover:
- get_portfolio_holdings()
- get_holding()
- get_portfolio_allocation_by_currency()
- get_holding_dividend_ratio_to_portfolio()
"""

import pytest
import datetime as dt
from backend.services.holding_service import HoldingService
from backend.repositories import (
    HoldingRepository,
    DividendPaymentRepository,
    StockRepository,
    PortfolioRepository,
    TransactionRepository
)
from backend.models import (
    StockData,
    PortfolioData,
    TransactionData,
    DividendPaymentData
)


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

@pytest.fixture(scope="function")
def repositories():
    """Create all repository instances."""
    return {
        'holding_repo': HoldingRepository(db_config),
        'div_payment_repo': DividendPaymentRepository(db_config),
        'stock_repo': StockRepository(db_config),
        'portfolio_repo': PortfolioRepository(db_config),
        'transaction_repo': TransactionRepository(db_config)
    }


@pytest.fixture
def service(repositories):
    """Create HoldingService with injected repositories."""
    return HoldingService(
        holding_repo=repositories['holding_repo'],
        div_payment_repo=repositories['div_payment_repo'],
        stock_repo=repositories['stock_repo']
    )


@pytest.fixture
def test_portfolio(repositories):
    """
    Create test portfolio and cleanup after.
    Cleans dividends and transactions before portfolio.
    """
    portfolio = PortfolioData(
        user_id=1,
        name="Test Portfolio HoldingService",
        currency="USD"
    )
    portfolio_id = repositories['portfolio_repo'].add(portfolio)

    yield portfolio_id

    # Cleanup dividends first
    try:
        payments = repositories['div_payment_repo'].get_by_portfolio(portfolio_id)
        for payment in payments:
            repositories['div_payment_repo'].delete(payment.id)
    except:
        pass

    # Then cleanup transactions
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
def test_stock_usd(repositories):
    """Create a USD test stock."""
    stock = StockData(
        ticker="TESTHOLD",
        company_name="Test Holding Corp",
        sector="Technology",
        industry="Software",
        currency="USD"
    )
    stock_id = repositories['stock_repo'].add(stock)

    yield stock_id

    # Cleanup transactions referencing this stock
    try:
        transactions = repositories['transaction_repo'].get_by_stock(stock_id)
        for transaction in transactions:
            repositories['transaction_repo'].delete(transaction.id)
    except:
        pass

    try:
        repositories['stock_repo'].delete(stock_id)
    except:
        pass


@pytest.fixture
def test_stock_eur(repositories):
    """Create a EUR test stock."""
    stock = StockData(
        ticker="THEUR",
        company_name="Test Holding Euro Corp",
        sector="Finance",
        industry="Banking",
        currency="EUR"
    )
    stock_id = repositories['stock_repo'].add(stock)

    yield stock_id

    # Cleanup transactions referencing this stock
    try:
        transactions = repositories['transaction_repo'].get_by_stock(stock_id)
        for transaction in transactions:
            repositories['transaction_repo'].delete(transaction.id)
    except:
        pass

    try:
        repositories['stock_repo'].delete(stock_id)
    except:
        pass


@pytest.fixture
def test_holding(repositories, test_portfolio, test_stock_usd):
    """
    Create a holding by inserting a BUY transaction.
    Holdings are calculated by the VIEW automatically.
    
    Yields:
        tuple: (portfolio_id, stock_id)
    """
    transaction = TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock_usd,
        type='BUY',
        quantity=10,
        price=100.0,
        fee=1.0
    )
    transaction_id = repositories['transaction_repo'].add(transaction)

    yield (test_portfolio, test_stock_usd)

    # Cleanup transaction
    try:
        repositories['transaction_repo'].delete(transaction_id)
    except:
        pass


@pytest.fixture
def test_dividend_payment(repositories, test_portfolio, test_stock_usd):
    """Create a test dividend payment."""
    payment = DividendPaymentData(
        portfolio_id=test_portfolio,
        stock_id=test_stock_usd,
        amount_per_share=0.5,
        total_amount=5.0,
        paid_at=dt.datetime.now(),
        ex_dividend_date=dt.datetime.now()
    )
    payment_id = repositories['div_payment_repo'].add(payment)

    yield payment_id

    try:
        repositories['div_payment_repo'].delete(payment_id)
    except:
        pass


# ==========================================
# TESTS - get_portfolio_holdings()
# ==========================================

def test_get_portfolio_holdings(service, test_holding):
    """Test getting all holdings for a portfolio."""
    portfolio_id, stock_id = test_holding

    holdings = service.get_portfolio_holdings(portfolio_id)

    assert len(holdings) > 0
    assert any(h.stock_id == stock_id for h in holdings)


def test_get_portfolio_holdings_empty(service, test_portfolio):
    """Test getting holdings for portfolio with no transactions."""
    holdings = service.get_portfolio_holdings(test_portfolio)

    assert holdings == []


# ==========================================
# TESTS - get_holding()
# ==========================================

def test_get_holding(service, test_holding):
    """Test getting a specific holding by composite key."""
    portfolio_id, stock_id = test_holding

    holding = service.get_holding(portfolio_id, stock_id)

    assert holding is not None
    assert holding.portfolio_id == portfolio_id
    assert holding.stock_id == stock_id
    assert holding.total_shares == 10
    assert holding.total_invested > 0


def test_get_holding_not_found(service, test_portfolio):
    """Test getting non-existent holding returns None."""
    holding = service.get_holding(test_portfolio, 999999)

    assert holding is None


# ==========================================
# TESTS - get_portfolio_allocation_by_currency()
# ==========================================

def test_get_portfolio_allocation_single_currency(
    service, repositories, test_portfolio, test_stock_usd
):
    """Test allocation with single currency (100% USD)."""
    # Create BUY transaction
    transaction = TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock_usd,
        type='BUY',
        quantity=10,
        price=100.0
    )
    transaction_id = repositories['transaction_repo'].add(transaction)

    # Get allocation
    allocation = service.get_portfolio_allocation_by_currency(test_portfolio)

    assert 'USD' in allocation
    assert abs(allocation['USD'] - 100.0) < 0.01  # ~100%

    # Cleanup
    repositories['transaction_repo'].delete(transaction_id)


def test_get_portfolio_allocation_multiple_currencies(
    service, repositories, test_portfolio, test_stock_usd, test_stock_eur
):
    """Test allocation with USD and EUR stocks."""
    # Buy USD stock (1000.0 invested)
    t1_id = repositories['transaction_repo'].add(TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock_usd,
        type='BUY',
        quantity=10,
        price=100.0
    ))

    # Buy EUR stock (500.0 invested)
    t2_id = repositories['transaction_repo'].add(TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock_eur,
        type='BUY',
        quantity=5,
        price=100.0
    ))

    # Get allocation
    allocation = service.get_portfolio_allocation_by_currency(test_portfolio)

    assert 'USD' in allocation
    assert 'EUR' in allocation
    assert abs(sum(allocation.values()) - 100.0) < 0.01  # Total = 100%
    assert allocation['USD'] > allocation['EUR']  # USD > EUR (invested more)

    # Cleanup
    repositories['transaction_repo'].delete(t1_id)
    repositories['transaction_repo'].delete(t2_id)


def test_get_portfolio_allocation_empty(service, test_portfolio):
    """Test allocation with no holdings returns empty dict."""
    allocation = service.get_portfolio_allocation_by_currency(test_portfolio)

    assert allocation == {}


def test_get_portfolio_allocation_returns_percentages(
    service, repositories, test_portfolio, test_stock_usd
):
    """Test that allocation values are percentages (0-100)."""
    transaction_id = repositories['transaction_repo'].add(TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock_usd,
        type='BUY',
        quantity=10,
        price=100.0
    ))

    allocation = service.get_portfolio_allocation_by_currency(test_portfolio)

    for currency, percentage in allocation.items():
        assert isinstance(percentage, float)
        assert 0 <= percentage <= 100

    # Cleanup
    repositories['transaction_repo'].delete(transaction_id)


# ==========================================
# TESTS - get_holding_dividend_ratio_to_portfolio()
# ==========================================

def test_get_holding_dividend_ratio(
    service, repositories, test_portfolio, test_stock_usd, test_holding
):
    """Test dividend ratio for a holding."""
    portfolio_id, stock_id = test_holding

    # Create dividend payments
    payment = DividendPaymentData(
        portfolio_id=portfolio_id,
        stock_id=stock_id,
        amount_per_share=0.5,
        total_amount=5.0,
        paid_at=dt.datetime.now(),
        ex_dividend_date=dt.datetime.now()
    )
    payment_id = repositories['div_payment_repo'].add(payment)

    # Get ratio
    ratio = service.get_holding_dividend_ratio_to_portfolio(portfolio_id)

    # Only one stock → 100%
    stock = repositories['stock_repo'].get_by_id(stock_id)
    assert stock.ticker in ratio
    assert abs(ratio[stock.ticker] - 100.0) < 0.01

    # Cleanup
    repositories['div_payment_repo'].delete(payment_id)


def test_get_holding_dividend_ratio_no_dividends(
    service, test_holding
):
    """Test dividend ratio with no dividends returns empty dict."""
    portfolio_id, stock_id = test_holding

    ratio = service.get_holding_dividend_ratio_to_portfolio(portfolio_id)

    assert ratio == {}


def test_get_holding_dividend_ratio_returns_percentages(
    service, repositories, test_portfolio, test_stock_usd, test_holding
):
    """Test that ratio values are percentages (0-100)."""
    portfolio_id, stock_id = test_holding

    # Create dividend payment
    payment_id = repositories['div_payment_repo'].add(DividendPaymentData(
        portfolio_id=portfolio_id,
        stock_id=stock_id,
        amount_per_share=0.5,
        total_amount=5.0,
        paid_at=dt.datetime.now(),
        ex_dividend_date=dt.datetime.now()
    ))

    ratio = service.get_holding_dividend_ratio_to_portfolio(portfolio_id)

    for ticker, percentage in ratio.items():
        assert isinstance(percentage, float)
        assert 0 <= percentage <= 100

    # Cleanup
    repositories['div_payment_repo'].delete(payment_id)


def test_get_holding_dividend_ratio_sum_to_100(
    service, repositories, test_portfolio, test_stock_usd,
    test_stock_eur, test_holding
):
    """Test that all ratios sum to ~100%."""
    portfolio_id, stock_id_usd = test_holding

    # Buy EUR stock too
    t_eur_id = repositories['transaction_repo'].add(TransactionData(
        portfolio_id=test_portfolio,
        stock_id=test_stock_eur,
        type='BUY',
        quantity=5,
        price=100.0
    ))

    # Create dividends for both stocks
    p1_id = repositories['div_payment_repo'].add(DividendPaymentData(
        portfolio_id=portfolio_id,
        stock_id=stock_id_usd,
        amount_per_share=0.5,
        total_amount=5.0,
        paid_at=dt.datetime.now(),
        ex_dividend_date=dt.datetime.now()
    ))

    p2_id = repositories['div_payment_repo'].add(DividendPaymentData(
        portfolio_id=portfolio_id,
        stock_id=test_stock_eur,
        amount_per_share=0.3,
        total_amount=3.0,
        paid_at=dt.datetime.now(),
        ex_dividend_date=dt.datetime.now()
    ))

    ratio = service.get_holding_dividend_ratio_to_portfolio(portfolio_id)

    assert abs(sum(ratio.values()) - 100.0) < 0.01  # Total ~100%
    assert len(ratio) == 2  # Two stocks

    # Cleanup
    repositories['div_payment_repo'].delete(p1_id)
    repositories['div_payment_repo'].delete(p2_id)
    repositories['transaction_repo'].delete(t_eur_id)


# ==========================================
# RUN TESTS
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
