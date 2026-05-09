import pytest
import datetime as dt
from backend.repositories import PortfolioRepository
from backend.models.portfolio import PortfolioData

db_config = {
    'host': 'localhost',
    'database': 'dividend_db',
    'user': 'dividend_user',
    'password': 'dividend123'
}


@pytest.fixture
def repo():
    return PortfolioRepository(db_config)


@pytest.fixture
def created_portfolio(repo):
    portfolio = PortfolioData(
        id=0,
        user_id=1,
        name="Test Portfolio",
        currency="EUR",
        created_at=dt.datetime.now()
    )
    portfolio_id = repo.add(portfolio)
    yield portfolio_id
    deleted = repo.get_by_id(portfolio_id)
    if deleted is not None:
        repo.delete(portfolio_id)


def test_add(repo):
    portfolio = PortfolioData(id=0, user_id=1, name="Test Add", currency="EUR")
    portfolio_id = repo.add(portfolio)
    assert isinstance(portfolio_id, int)
    repo.delete(portfolio_id)


def test_get_by_id(repo, created_portfolio):
    fetched = repo.get_by_id(created_portfolio)
    assert fetched is not None
    assert fetched.name == "Test Portfolio"
    assert fetched.currency == "EUR"


def test_get_by_id_not_found(repo):
    assert repo.get_by_id(999999) is None


def test_get_by_user(repo, created_portfolio):
    portfolios = repo.get_by_user(1)
    assert any(p.id == created_portfolio for p in portfolios)


def test_get_all(repo, created_portfolio):  # noqa: ARG001
    all_portfolios = repo.get_all()
    assert len(all_portfolios) > 0


def test_update(repo, created_portfolio):
    fetched = repo.get_by_id(created_portfolio)
    fetched.name = "Portfolio Modifié"
    repo.update(fetched)
    updated = repo.get_by_id(created_portfolio)
    assert updated.name == "Portfolio Modifié"


def test_delete(repo):
    portfolio = PortfolioData(id=0, user_id=1, name="Test Delete", currency="USD")
    portfolio_id = repo.add(portfolio)
    repo.delete(portfolio_id)
    assert repo.get_by_id(portfolio_id) is None
