from typing import Protocol, TypeVar
import datetime as dt

from backend.models.dividend_payment import DividendPaymentData
from backend.models.holding import HoldingData
from backend.models.portfolio import PortfolioData
from backend.models.stock import StockData
from backend.models.transaction import TransactionData

T = TypeVar('T')

class Repository(Protocol[T]):
    """All repositories implement at least theses methods"""
    
    def add(self, model: T) -> int: ...
    
    
    def get_by_id(self, id: int) -> T | None: ...
    
    
    def get_all(self) -> list[T]: ...
    
    
    def update(self, model: T) -> None: ...
    
    
    def delete(self, id: int) -> None: ...
    
    
    
class StockRepositoryProtocol(Repository[StockData], Protocol):
    """Protocol for StockRepository with specific methods"""
    
    #Inheritated CRUD
    
    #Specific methods
    def get_by_ticker(self, ticker: str) -> StockData | None: ...
    
    
    def search_by_sector(self, sector: str) -> list[StockData]: ...
    
    
class PortfolioRepositoryProtocol(Repository[PortfolioData], Protocol):
    #Inheritated CRUD
    
    #Specific methods
    def get_by_user(self, user_id: int) -> list[PortfolioData]: ...
    

class TransactionRepositoryProtocol(Repository[TransactionData], Protocol):
    #Inheritated CRUD
    
    #Specific methods
    def get_by_portfolio(self, portfolio_id: int) -> list[TransactionData]: ...
    
    
    def get_by_stock(self, stock_id: int) -> list[TransactionData]: ...
 
#Only inheritates from Protocol ONLY because it's a VIEW, not a TABLE  
class HoldingRepositoryProtocol(Protocol):
    
    #Specific methods
    def get_by_portfolio(self, portfolio_id: int) -> list[HoldingData]: ...
    
    
    def get_by_id(self, portfolio_id: int, stock_id: int) -> HoldingData | None: ...
    
class DividendPaymentRepositoryProtocol(Repository[DividendPaymentData], Protocol):
    
    #Inheritated CRUD
    
    #Specific methods
    def get_by_portfolio(self, portfolio_id: int) -> list[DividendPaymentData]: ...
    
    
    def get_by_stock(self, stock_id: int) -> list[DividendPaymentData]: ...
    
    
    def get_by_date_range(self, start: dt.datetime, end: dt.datetime) -> list[DividendPaymentData]: ...
    
    
    
    

    
    
    