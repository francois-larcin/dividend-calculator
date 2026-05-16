from backend.models import (
    StockData
)

from backend.repositories import (
    StockRepository
)

import datetime as dt

class StockService:
    def __init__(self, stock_repo: StockRepository):
        self.stock_repo = stock_repo
        
    # ==========================================
    # SIMPLE DELEGATION (just pass to repository)
    # ==========================================
    
    def create_stock(
        self,
        ticker: str,
        company_name: str,
        sector: str,
        industry: str,
        currency: str
        ) -> int:
        """
        Create a new stock 
        
        Simple delegation - just creates the model and calls repository
        """
        stock = StockData(
            ticker=ticker.upper(),
            company_name=company_name,
            sector=sector,
            industry=industry,
            currency=currency,
            last_update_at=dt.datetime.now()
        )
        
        return self.stock_repo.add(stock)
        
        
    def get_stock(self, stock_id: int) -> StockData | None:
        return self.stock_repo.get_by_id(stock_id)
    
    
    def get_all_stocks(self) -> list[StockData]:
        return self.stock_repo.get_all()
    
    
    def update_stock(self, stock: StockData) -> None:
        self.stock_repo.update(stock)
    
    
    def delete_stock(self, stock_id: int) -> None:
        self.stock_repo.delete(stock_id)
    
    
    def get_stocks_by_sector(self, sector: str) -> list[StockData]:
        return self.stock_repo.search_by_sector(sector)
        
    
    def get_stocks_by_ticker(self, ticker: str) -> StockData | None:
        return self.stock_repo.get_by_ticker(ticker)
        
        
        
