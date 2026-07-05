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
    TransactionService, 
    DividendPaymentService
)

import yfinance as yf

class HoldingService: 
    def __init__(
        self, 
        holding_repo: HoldingRepository,
        stock_repo: StockRepository,
        div_payment_repo: DividendPaymentRepository,
        stock_service: StockService,
        transaction_service: TransactionService,
        div_payment_service : DividendPaymentService
        ):
        self.holding_repo = holding_repo
        self.stock_repo = stock_repo
        self.div_payment_repo = div_payment_repo
        self.stock_service = stock_service
        self.transaction_service = transaction_service
        self.div_payment_service = div_payment_service
        
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
        
    def get_holdings_dividend_ratio_to_portfolio(
        self, 
        portfolio_id: int,
        portfolio_total_dividends: float
        ) -> dict[str, float]:
        """
        For each holding of a portfolio, calculate holding total dividend received to portfolio CURRENT total dividend
        
        Ex : this holding got me 13% of all my dividends for this portfolio
        """
        
        #Current holdings in portfolio ONLY 
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        by_ticker = {}
        
        for h in holdings:
            
            by_ticker[h.ticker] = self._get_holding_dividend_ratio_to_portfolio(portfolio_id, h.stock_id, portfolio_total_dividends)
        
        return by_ticker
        
    def _get_holding_dividend_ratio_to_portfolio(
        self, 
        portfolio_id:int,
        stock_id:int,
        portfolio_total_dividends: float
    ) -> float:
        """
        For a holding, calculate holding total dividend received to portfolio CURRENT total dividend
        
        Ex : this holding got me 13% of all my dividends for this portfolio
        """
        
        # 1. Get total div received for this holding
        holding_total_div = self.div_payment_service.get_total_dividend_received_by_stock(portfolio_id, stock_id)
        
        if holding_total_div > 0 and portfolio_total_dividends > 0:
            return holding_total_div / portfolio_total_dividends * 100
        else:
            return 0.0
        
        
    def get_all_holdings_detail(self, portfolio_id: int) -> list[dict]:
        """Get portfolio holdings with full detail (gain, description, dividend ratio to portfolio, ...)"""
        
        # 1. Get holdings
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        # 2. Fetch all current prices ONCE
        prices = {}
        for h in holdings:
            prices[h.stock_id] = self.stock_service.get_current_price(h.ticker)
        
        # 3. Calculate totals ONCE 
        portfolio_current_value = sum(
            h.current_value(prices[h.stock_id]) for h in holdings
            )
        
        portfolio_total_dividends = self.div_payment_service.get_total_dividend_received_by_portfolio(portfolio_id)
        
        # 4. Enrich EACH holding
        return [
            self.get_holding_detail(h, prices[h.stock_id], portfolio_current_value, portfolio_total_dividends)
            for h in holdings
        ]
    
    def get_holding_detail(
        self,
        h: HoldingData,
        current_price: float,
        portfolio_current_value: float,
        portfolio_total_dividends: float
    ) -> dict:
        """Get holding with full detailed informations"""
        
        # 1. Get portfolio_id & stock_id from holding
        portfolio_id = h.portfolio_id
        stock_id = h.stock_id
        
        # 2. Get holding infos
        unrealized_gain = h.unrealized_gain(current_price)
        unrealized_gain_percent = h.gain_percentage(current_price)
        current_value = h.current_value(current_price)
        total_invested = h.total_invested
        realized_gain = self.transaction_service.get_realized_gain_by_portfolio_and_stock(portfolio_id, stock_id)
        description = yf.Ticker(h.ticker).info.get('longBusinessSummary')
        weight = (current_value / portfolio_current_value * 100) if portfolio_current_value > 0 else 0.0
        dividend_ratio = self._get_holding_dividend_ratio_to_portfolio(portfolio_id, stock_id, portfolio_total_dividends)
        
        # 3. Convert HoldingData into dict to enrich it
        h_dict = asdict(h)
        h_dict["stock_price"] = current_price
        h_dict["current_value"] = current_value
        h_dict["gain"] = unrealized_gain
        h_dict["gain_percent"] = unrealized_gain_percent
        h_dict["total_invested"] = total_invested
        h_dict["realized_gain"] = realized_gain
        h_dict["description"] = description
        h_dict["weight"] = weight
        h_dict["dividend_ratio"] = dividend_ratio
        
        # 4. Return enriched dict
        return h_dict
    
    def get_one_holding_detail(self, portfolio_id:int, stock_id:int) -> dict | None:
        """Calculate all needed totals and call get_holding_detail()"""
        
        holding = self.get_holding(portfolio_id, stock_id)
        if holding is None:
            return None
        
        #Calculate needed totals
        current_price = self.stock_service.get_current_price(holding.ticker)
        
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        prices = {h.stock_id: self.stock_service.get_current_price(h.ticker) for h in holdings}
        portfolio_current_value = sum(h.current_value(prices[h.stock_id]) for h in holdings)
        
        portfolio_total_dividends = self.div_payment_service.get_total_dividend_received_by_portfolio(portfolio_id)
        
        return self.get_holding_detail(holding, current_price, portfolio_current_value, portfolio_total_dividends)
        
        