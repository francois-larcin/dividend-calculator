import pytest
import datetime as dt
from backend.services.dividend_payment_service import DividendPaymentService
from backend.services.portfolio_service import PortfolioService
from backend.repositories import (
    DividendPaymentRepository,
    StockRepository,
    PortfolioRepository,
    HoldingRepository,
    TransactionRepository
)
from backend.models.dividend_payment import DividendPaymentData

db_config = {
    'host': 'localhost',
    'database': 'dividend_db',
    'user': 'dividend_user',
    'password': 'dividend123'
}


@pytest.fixture
def repositories():
    return {
        'div_payment_repo': DividendPaymentRepository(db_config),
        'stock_repo': StockRepository(db_config),
        'portfolio_repo': PortfolioRepository(db_config),
        'holding_repo': HoldingRepository(db_config),
        'transaction_repo': TransactionRepository(db_config)
    }


@pytest.fixture
def services(repositories):
    portfolio_service = PortfolioService(
        portfolio_repo=repositories['portfolio_repo'],
        holding_repo=repositories['holding_repo'],
        transaction_repo=repositories['transaction_repo'],
    )

    dividend_service = DividendPaymentService(
        div_payment_repo=repositories['div_payment_repo'],
        stock_repo=repositories['stock_repo'],
        portfolio_repo=repositories['portfolio_repo'],
        portfolio_service=portfolio_service
    )

    return {
        'dividend_service': dividend_service,
        'portfolio_service': portfolio_service
    }


@pytest.fixture
def created_dividend_payment(repositories):
    div_payment = DividendPaymentData(
        id=0,
        portfolio_id=1,
        stock_id=1,
        amount_per_share=0.5,
        total_amount=5.0,
        paid_at=dt.datetime.now(),
        ex_dividend_date=dt.datetime.now()
    )
    div_payment_id = repositories['div_payment_repo'].add(div_payment)
    yield div_payment_id
    deleted = repositories['div_payment_repo'].get_by_id(div_payment_id)
    if deleted is not None:
        repositories['div_payment_repo'].delete(div_payment_id)


def test_create_div_payment(services):
    div_id = services['dividend_service'].create_div_payment(
        portfolio_id=1,
        stock_id=1,
        amount_per_share=0.75,
        total_amount=7.5,
        ex_dividend_date=dt.datetime.now()
    )
    assert isinstance(div_id, int)
    services['dividend_service'].delete_div_payment(div_id)


def test_get_dividend_payment(services, created_dividend_payment):
    fetched = services['dividend_service'].get_dividend_payment(created_dividend_payment)
    assert fetched is not None
    assert fetched.portfolio_id == 1
    assert fetched.stock_id == 1


def test_get_dividend_payment_not_found(services):
    assert services['dividend_service'].get_dividend_payment(999999) is None


def test_get_portfolio_div_payment(services, created_dividend_payment):
    payments = services['dividend_service'].get_portfolio_div_payment(1)
    assert any(p.id == created_dividend_payment for p in payments)


def test_get_by_portfolio_stock_div_payment(services, created_dividend_payment):
    payments = services['dividend_service'].get_by_portfolio_stock_div_payment(1, 1)
    assert any(p.id == created_dividend_payment for p in payments)


def test_update_div_payment(services, created_dividend_payment):
    fetched = services['dividend_service'].get_dividend_payment(created_dividend_payment)
    fetched.amount_per_share = 1.0
    services['dividend_service'].update_div_payment(fetched)
    updated = services['dividend_service'].get_dividend_payment(created_dividend_payment)
    assert updated.amount_per_share == 1.0


def test_delete_div_payment(services):
    div_id = services['dividend_service'].create_div_payment(
        portfolio_id=1,
        stock_id=1,
        amount_per_share=0.5,
        total_amount=5.0,
        ex_dividend_date=dt.datetime.now()
    )
    services['dividend_service'].delete_div_payment(div_id)
    assert services['dividend_service'].get_dividend_payment(div_id) is None


def test_get_total_dividend_received_by_portfolio(services, created_dividend_payment):
    total = services['dividend_service'].get_total_dividend_received_by_portfolio(1)
    assert isinstance(total, float)
    assert total > 0


def test_get_total_dividend_received_by_stock(services, created_dividend_payment):
    total = services['dividend_service'].get_total_dividend_received_by_stock(1, 1)
    assert isinstance(total, float)
    assert total > 0


def test_calculate_portfolio_dividend_yield(services, created_dividend_payment):
    yield_value = services['dividend_service'].calculate_portfolio_dividend_yield(1)
    assert isinstance(yield_value, float)
    assert yield_value >= 0


def test_calculate_stock_dividend_yield(services, created_dividend_payment):
    yield_value = services['dividend_service'].calculate_stock_dividend_yield(1, 1)
    assert isinstance(yield_value, float)
    assert yield_value >= 0
