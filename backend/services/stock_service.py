from dataclasses import asdict

from backend.models import (
    StockData
)

from backend.repositories import (
    StockRepository
)

import datetime as dt
import yfinance as yf
import requests

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
    
    def refresh_from_yfinance(self, stock_id: int) -> StockData | None: 
        
        #1. Check that stock exists
        stock = self.stock_repo.get_by_id(stock_id)
        if stock is None:
            return None
        
        #2. Fetch new data 
        
        
    
    
    #full live search
    def search_stocks(self, query: str) -> list[dict]:
        """Search in DB first, then yfinance if not found"""
        # 1. Search in DB
        local = self.stock_repo.search_by_name(query)
        local_dicts = [
                {
                    'ticker': s.ticker,
                    'company_name': s.company_name,
                }
                for s in local
        ]
        
        # Ticker already found in DB
        local_tickers = {s.ticker for s in local}
        
        # 2. Search in yfinance
        yf_results = self._search_yfinance(query)
        
            
        # 3. Combine both searches without doubled results
        yf_filtered = [
            r for r in yf_results
            if r.get('ticker') not in local_tickers
        ]
        
        return (local_dicts + yf_filtered)
    

    # ==========================================
    # HELPER private
    # ==========================================
    
    def _search_yfinance(self, query: str) -> list[dict]:
        """
        Search stocks via yfinance
        
        Private helper method
        
        Returns:
            List of dicts with ticker and company_name
        """
        
        try:
            results = yf.Search(query).quotes
            
            return [
                {
                    'ticker': r.get('symbol'),
                    'company_name': r.get('longname') or r.get('shortname'),
                }
                for r in results[:10]
            ]
        #Several types of possible exception
        except requests.exceptions.RequestException:
            return []
         
        
