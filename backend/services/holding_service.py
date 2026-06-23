from dataclasses import asdict

from backend.models import (
    HoldingData
)

from backend.repositories import (
    HoldingRepository,
    StockRepository,
    DividendPaymentRepository
)

from backend.services import (
    StockService,
    TransactionService
)

class HoldingService: 
    def __init__(
        self, 
        holding_repo: HoldingRepository,
        stock_repo: StockRepository,
        div_payment_repo: DividendPaymentRepository,
        stock_service: StockService,
        transaction_service: TransactionService
        ):
        self.holding_repo = holding_repo
        self.stock_repo = stock_repo
        self.div_payment_repo = div_payment_repo
        self.stock_service = stock_service
        self.transaction_service = transaction_service
        
    # ==========================================
    # SIMPLE DELEGATION (just pass to repository)
    # ==========================================  
    
    def get_portfolio_holdings(self, portfolio_id: int) -> list[HoldingData]:
        """Get all the holdings for a portfolio"""
        return self.holding_repo.get_by_portfolio(portfolio_id)
    
    
    def get_holding(self, portfolio_id: int, stock_id: int) -> HoldingData | None:
        """Get a holding in a portfolio"""
        return self.holding_repo.get_by_id(portfolio_id, stock_id)
    
    
    # ==========================================
    # BUSINESS LOGIC - ANALYSE
    # ==========================================
    
    
    def get_portfolio_allocation_by_sector(self, portfolio_id: int) -> dict[str, float]:
        """Calculate portfolio allocation by sector
        
        Business logic, not calculated by VIEW
        """
        
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        total = sum(h.total_invested for h in holdings)
        if total == 0:
            return {}
        
        by_sector = {}
        
        for holding in holdings:
            stock = self.stock_repo.get_by_id(holding.stock_id)
            sector = stock.sector if stock else 'Unknown'
            by_sector[sector] = by_sector.get(sector, 0) + holding.total_invested
        
        return {
            sector: float(value / total * 100)
            for sector, value in by_sector.items()
        }
        
        
    def get_portfolio_allocation_by_currency(self, portfolio_id: int) -> dict[str, float]:
        """Calculate portfolio allocation by currency"""
        
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        total = sum(h.total_invested for h in holdings)
        if total == 0:
            return {}
        
        by_currency = {}
        
        for holding in holdings:
            currency = holding.currency
            #print(f"Currency : {currency}")
            by_currency[currency] = by_currency.get(currency, 0) + holding.total_invested
            
        return {
            currency: float(value / total * 100)
            for currency, value in by_currency.items()
        }
        
    def get_holding_dividend_history(
        self,
        portfolio_id: int,
        stock_id: int,
    ) -> dict | None:
        """
        Get holding with its dividend history
        
        Composition - not calculated by VIEW
        """
        holding = self.holding_repo.get_by_id(portfolio_id, stock_id)
        if not holding:
            return None
        
        dividends = self.div_payment_repo.get_by_stock(stock_id)
        
        return {
            'holding': holding,
            'dividends': dividends
        }
        
    def get_holding_dividend_ratio_to_portfolio(self, portfolio_id: int) -> dict[str, float]:
        """
        For each holding of a portfolio, calculate holding total dividend received to portfolio total dividend
        
        Ex : this holding got me 13% of all my dividends for this portfolio
        """
        
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        all_payments = self.div_payment_repo.get_by_portfolio(portfolio_id)
        total = sum(dp.total_amount for dp in all_payments)
        if total == 0:
            return {}

        
        by_ticker = {}
        
        for holding in holdings:
            holding_payments = self.div_payment_repo.get_by_portfolio_and_stock(portfolio_id, holding.stock_id)
            holding_total_div = sum(dp.total_amount for dp in holding_payments)
            
            by_ticker[holding.ticker] = holding_total_div
            
        return {
            ticker: float(value / total * 100)
            for ticker, value in by_ticker.items()
        }
        
    def get_holding_with_gain(self, portfolio_id: int) -> list[dict]:
        """Get holdings with current value and gain calculated"""
        
        # 1. Get holdings
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        result = []
        
        
        for h in holdings:
            # 2. For each holding, fetch yfinance price
            current_price = self.stock_service.get_current_price(h.ticker)
            
            # 3. Calculate unrealized gain & gain_percent, current_value and total_invested
            unrealized_gain = h.unrealized_gain(current_price)
            unrealized_gain_percent = h.gain_percentage(current_price)
            current_value = h.current_value(current_price)
            total_invested = h.total_invested
            
            #4 Calculate realized gain
            realized_gain = self.transaction_service.get_realized_gain_by_portfolio_and_stock(portfolio_id, h.stock_id)
            
            # 5. Convert HoldingData into dict so I can enrich it
            holding_dict = asdict(h)
            holding_dict["stock_price"] = current_price
            holding_dict["current_value"] = current_value
            holding_dict["gain"] = unrealized_gain
            holding_dict["gain_percent"] = unrealized_gain_percent
            holding_dict["total_invested"] = total_invested
            holding_dict["realized_gain"] = realized_gain
            
            result.append(holding_dict)
            #print(holding_dict)
            
        # 4. Return enriched dicts list
        return result