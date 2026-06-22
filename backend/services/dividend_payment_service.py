from backend.models import (
    PortfolioData,
    DividendPaymentData,
    StockData
)

from backend.repositories import (
    PortfolioRepository,
    StockRepository, 
    DividendPaymentRepository,
    HoldingRepository
)

import datetime as dt
import yfinance as yf

from backend.services.portfolio_service import PortfolioService

class DividendPaymentService:
    def __init__(
        self,
        div_payment_repo: DividendPaymentRepository,
        stock_repo: StockRepository,
        portfolio_repo: PortfolioRepository,
        holding_repo: HoldingRepository,
        portfolio_service: PortfolioService,
        ):
        self.div_payment_repo = div_payment_repo
        self.stock_repo = stock_repo
        self.portfolio_repo = portfolio_repo
        self.holding_repo = holding_repo
        self.portfolio_service = portfolio_service
        
    # ==========================================
    # SIMPLE DELEGATION (just pass to repository)
    # ==========================================
    
    def get_dividend_payment(self, div_payment_id: int) -> DividendPaymentData | None:
        return self.div_payment_repo.get_by_id(div_payment_id)
    
    
    def get_portfolio_div_payment(self, portfolio_id: int) -> list[DividendPaymentData] : 
        return self.div_payment_repo.get_by_portfolio(portfolio_id)
    
    
    def get_by_portfolio_stock_div_payment(self, portfolio_id: int, stock_id: int) -> list[DividendPaymentData]:
        return self.div_payment_repo.get_by_portfolio_and_stock(portfolio_id, stock_id)
    
    
    def get_by_stock(self, stock_id: int) -> list[DividendPaymentData]:
        return self.div_payment_repo.get_by_stock(stock_id)
    
    
    def get_by_portfolio_and_date_range(self, portfolio_id: int, start_date: dt.date, end_date: dt.date) -> list[DividendPaymentData]:
        return self.div_payment_repo.get_by_portfolio_and_date_range(portfolio_id, start_date, end_date)
         
            
    def delete_div_payment(self, div_payment_id: int) -> None:
        self.div_payment_repo.delete(div_payment_id)
    
    
    # ==========================================
    # BUSINESS LOGIC - CALCULATION 
    # ==========================================
    
    def get_total_dividend_received_by_portfolio(self, portfolio_id: int) -> float:
        list_div_payments = self.div_payment_repo.get_by_portfolio(portfolio_id)
        
        return float(sum(dp.total_amount for dp in list_div_payments))
 
 
    def get_total_dividend_received_by_stock(self, portfolio_id: int, stock_id: int) -> float:
        list_div_payments = self.div_payment_repo.get_by_portfolio_and_stock(portfolio_id, stock_id)
        
        return float(sum(dp.total_amount for dp in list_div_payments))
 
 
    def calculate_portfolio_dividend_yield(self, portfolio_id: int) -> float:
        
        total_div_received = self.get_total_dividend_received_by_portfolio(portfolio_id)
        
        filled_portfolio = self.portfolio_service.get_portfolio_with_holdings(portfolio_id)
        if filled_portfolio is None:
            return 0.0
        
        total_invested = filled_portfolio.total_invested()
        if total_invested == 0:
            return 0.0
        
        return float((total_div_received / total_invested) * 100)
    
    
    def calculate_stock_dividend_yield(self, portfolio_id: int, stock_id: int) -> float:
        
        total_div_received = self.get_total_dividend_received_by_stock(portfolio_id, stock_id)
        
        stock = self.stock_repo.get_by_id(stock_id)
        if stock is None:
            return 0.0
        
        filled_portfolio = self.portfolio_service.get_portfolio_with_holdings(portfolio_id)
        if filled_portfolio is None:
            return 0.0
        
        holding = filled_portfolio.find_holding_by_ticker(stock.ticker)
        if holding is None:
            return 0.0
        
        if holding.total_invested == 0:
            return 0.0
        
        return float((total_div_received / holding.total_invested) * 100)
       
        
    def sync_dividends(self, portfolio_id: int) -> int:
        """
        Sync dividend payments from yfinance for all holdings.
        
        Returns:
            Number of new dividends inserted
        """
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        new_dividends = 0
        
        for holding in holdings:
                        
            #Fetch dividend history from yfinance
            yf_stock = yf.Ticker(holding.ticker)
            dividends = yf_stock.dividends #pandas Series with date and amount
            
            dividends = dividends[dividends.index.date >= holding.date_added.date()]
            
            #Check if this dividend alreay exists in DB
            existing = self.div_payment_repo.get_by_portfolio_and_stock(portfolio_id, holding.stock_id)
            existing_dates = [d.ex_dividend_date for d in existing]
            
            for date, amount in dividends.items():
                
                ex_dividend_date = date.date()
                
                #Add only if not yet in DB
                if ex_dividend_date not in existing_dates:
                    payment = DividendPaymentData(
                        portfolio_id=portfolio_id,
                        stock_id=holding.stock_id,
                        amount_per_share=float(amount),
                        total_amount=float(amount * holding.total_shares),
                        paid_at=ex_dividend_date,                           #Approximation
                        ex_dividend_date=ex_dividend_date
                    )
                    self.div_payment_repo.add(payment)
                    new_dividends += 1
                    
        return new_dividends
        
        
        
        
        
        
    
    
    
        