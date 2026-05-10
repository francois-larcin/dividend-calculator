from backend.models import (
    PortfolioData,
    DividendPaymentData,
    StockData
)

from backend.repositories import (
    PortfolioRepository,
    StockRepository, 
    DividendPaymentRepository
)

import datetime as dt

from backend.services.portfolio_service import PortfolioService

class DividendPaymentService:
    def __init__(
        self,
        div_payment_repo: DividendPaymentRepository,
        stock_repo: StockRepository,
        portfolio_repo: PortfolioRepository,
        portfolio_service: PortfolioService
        ):
        self.div_payment_repo = div_payment_repo
        self.stock_repo = stock_repo
        self.portfolio_repo = portfolio_repo
        self.portfolio_service = portfolio_service
        
    # ==========================================
    # SIMPLE DELEGATION (just pass to repository)
    # ==========================================
    
    def create_div_payment(
        self,
        portfolio_id: int,
        stock_id: int,
        amount_per_share: float,
        total_amount: float,
        ex_dividend_date: dt.datetime
    ) -> int:
        """
        Create a new dividend payment
        
        Simple delegation - just creates the model and calls repository
        """
        
        dividend_payment = DividendPaymentData(
            id=0, #TODO to be assigned by DB
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            amount_per_share=amount_per_share,
            total_amount=total_amount,
            paid_at=dt.datetime.now(),
            ex_dividend_date=ex_dividend_date
        )
        
        return self.div_payment_repo.add(dividend_payment)
    
    
    def get_dividend_payment(self, div_payment_id: int) -> DividendPaymentData | None:
        return self.div_payment_repo.get_by_id(div_payment_id)
    
    
    def get_portfolio_div_payment(self, portfolio_id: int) -> list[DividendPaymentData] : 
        return self.div_payment_repo.get_by_portfolio(portfolio_id)
    
    
    def get_by_portfolio_stock_div_payment(self, portfolio_id: int, stock_id: int) -> list[DividendPaymentData]:
        return self.div_payment_repo.get_by_portfolio_and_stock(portfolio_id, stock_id)
    
    
    def get_by_stock(self, stock_id: int) -> list[DividendPaymentData]:
        return self.div_payment_repo.get_by_stock(stock_id)
    
    
    def get_by_date_range(self, start_date: dt.datetime, end_date: dt.datetime) -> list[DividendPaymentData]:
        return self.div_payment_repo.get_by_date_range(start_date, end_date)
    
    
    def update_div_payment(self, div_payment: DividendPaymentData) -> None:
        self.div_payment_repo.update(div_payment)
    
        
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
        
        
        
        
        
        
        
    
    
    
        