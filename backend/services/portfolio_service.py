from backend.models import (
    PortfolioData,
    TransactionData
)

from backend.repositories import (
    PortfolioRepository,
    HoldingRepository,
    TransactionRepository
)
import datetime as dt


class PortfolioService:
    def __init__(
        self,
        portfolio_repo: PortfolioRepository,
        holding_repo: HoldingRepository,
        transaction_repo: TransactionRepository
        ):
        self.portfolio_repo = portfolio_repo
        self.holding_repo = holding_repo
        self.transaction_repo = transaction_repo
        
    # ==========================================
    # SIMPLE DELEGATION (just pass to repository)
    # ==========================================
    
    def create_portfolio(
        self, 
        user_id: int,
        name: int,
        currency: str
    ) -> int:
        """
        Create a new portfolio
        
        Simple delegation - just creates the model and calls repository
        """
        portfolio = PortfolioData(
            id=0, #TODO To be assigned by DB
            user_id=user_id,
            name=name,
            currency=currency,
            created_at=dt.datetime.now()
        )
        
        return self.portfolio_repo.add(portfolio)
    
    def get_portfolio(self, portfolio_id: int) -> PortfolioData | None:
        return self.portfolio_repo.get_by_id(portfolio_id)
    
    
    def get_user_portfolios(self, user_id: int) -> list[PortfolioData] : 
        return self.portfolio_repo.get_by_user(user_id)
    
    
    def update_portfolio(self, portfolio: PortfolioData) -> None:
        self.portfolio_repo.update(portfolio)
        
    def delete_portfolio(self, portfolio_id: int) -> None:
        self.portfolio_repo.delete(portfolio_id)


    # ==========================================
    # BUSINESS LOGIC - COMPOSITION 
    # ==========================================
    
    def get_portfolio_with_holdings(
        self, 
        portfolio_id: int,
    ) -> PortfolioData | None:
        """
        Get portfolio with its holdings loaded
        
        Steps: 
        1. Load portfolio from portfolio_repo
        2. Load holdings from holding_repo
        3. Compose them together
        """
        
        # 1. Get the portfolio
        portfolio = self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            return None
        
        # 2. Get the holdings for this portfolio
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        # 3. Compose - fill the holdings attribute
        portfolio.holdings = holdings
        
        return portfolio
    
    
    # ==========================================
    # BUSINESS LOGIC - CALCULATION 
    # ==========================================
    
    def calculate_portfolio_value(
        self,
        portfolio_id: int,
        current_prices: dict[int, float]
    ) -> float:
        """
        Calculate total portfolio value based on current prices
        
        Args:
            portfolio_id: Portfolio to calculate
            current_price : Dict mapping stock_id -> current_price
            
        Returns:
            Total portfolio value in portfolio currency
            
        """
        holdings = self.holding_repo.get_by_portfolio(portfolio_id)
        
        total_value = 0.0
        for holding in holdings:
            current_price = current_prices.get(holding.stock_id, 0)
            holding_value = holding.current_value(current_price)
            total_value += holding_value
            
        return total_value
    
    def calculate_portfolio_gain(
        self, 
        portfolio_id: int,
        current_prices: dict[int, float]
    ) -> dict:
        """
        Calculate portfolio P/L
        
        Returns:
            Dict with 'total_invested', 'current_value', 'gain', 'gain_percent'
        """
        portfolio = self.get_portfolio_with_holdings(portfolio_id)
        if portfolio is None:
            return {}
        
        total_invested = portfolio.total_invested()
        current_value = portfolio.current_value(current_prices)
        
        gain = current_value - total_invested
        gain_percent = (gain / total_invested * 100) if total_invested > 0 else 0
        
        return {
            'total_invested': total_invested,
            'current_value': current_value,
            'gain': gain,
            'gain_percent': gain_percent
        }
        
        
    # ==========================================
    # BUSINESS LOGIC - ORCHESTRATION
    # ==========================================
    
    def buy_stock(
        self,
        portfolio_id: int,
        stock_id: int, 
        quantity: float,
        price: float,
        fee: float = 0.0
    ) -> int:
        """
        Add stock to portfolio by creating a BUY transaction
        
        Uses transaction_repo to create transaction.
        The holding is automatically updated via the current_holdings VIEW
        """
        
        transaction = TransactionData(
            id=0,
            portfolio_id=portfolio_id,
            stock_id= stock_id,
            type= 'BUY',
            quantity=quantity,
            price=price,
            fee=fee,
            transaction_date=dt.datetime.now()
        )
        
        return self.transaction_repo.add(transaction)
    
    
    def sell_stock(
        self,
        portfolio_id: int,
        stock_id: int,
        quantity: float,
        price: float,
        fee: float = 0.0
    ) -> int:
        """Sell stock from portfolio by creating a SELL transaction"""
        
        transaction= TransactionData(
            id=0,
            portfolio_id=portfolio_id,
            stock_id= stock_id,
            type= 'BUY',
            quantity=quantity,
            price=price,
            fee=fee,
            transaction_date=dt.datetime.now()
        )
        
        return self.transaction_repo.add(transaction)
    
    # ==========================================
    # TESTS
    # ==========================================
    
if __name__ == "__main__":
    # Setup (normally done in Flask app initialization)
    db_config = {
        'host': 'localhost',
        'database': 'dividend_db',
        'user': 'dividend_user',
        'password': 'dividend123'
    }
    
    # Create repositories
    portfolio_repo = PortfolioRepository(db_config)
    holding_repo = HoldingRepository(db_config)
    transaction_repo = TransactionRepository(db_config)
    
    # Create service (DEPENDENCY INJECTION)
    service = PortfolioService(
        portfolio_repo=portfolio_repo,
        holding_repo=holding_repo,
        transaction_repo=transaction_repo
    )
    
    # Use the service
    portfolio_id = service.create_portfolio(
        user_id=1,
        name="My Dividend Portfolio",
        currency="USD"
    )
    
    print(f"Created portfolio: {portfolio_id}")
    
    # Get portfolio with holdings
    portfolio = service.get_portfolio_with_holdings(portfolio_id)
    print(f"Portfolio has {len(portfolio.holdings)} holdings")   
        
            
        
    
    