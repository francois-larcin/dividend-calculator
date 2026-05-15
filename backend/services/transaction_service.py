from backend.models import (
    TransactionData,
    StockData
)

from backend.repositories import (
    TransactionRepository,
    PortfolioRepository,
    StockRepository,
    HoldingRepository
)

import datetime as dt
import yfinance as yf


def map_yfinance_to_stock(ticker: str, yf_info: dict) -> StockData:
    """
    Convert yfinance info to StockData.
    
    Args:
        ticker: Stock ticker symbol
        yf_info: yfinance stock.info dict
    
    Returns:
        StockData instance
    """
    
    return StockData(
        ticker=yf_info.get('symbol', ticker).upper(),
        company_name=yf_info.get('longName', ticker),
        sector=yf_info.get('sector', 'Unknown'),
        industry=yf_info.get('industry', 'Unknown'),
        currency= yf_info.get('currency', 'USD'),
        last_update_at=dt.datetime.now()
    )
    
    
class TransactionService:
    def __init__(
        self, 
        transaction_repo: TransactionRepository, 
        portfolio_repo: PortfolioRepository,
        stock_repo: StockRepository,
        holding_repo: HoldingRepository
        ):
        self.transaction_repo = transaction_repo
        self.portfolio_repo = portfolio_repo
        self.stock_repo = stock_repo
        self.holding_repo = holding_repo
        
    # ==========================================
    # SIMPLE DELEGATION (just pass to repository)
    # ========================================== 
    
    def create_transaction(self, transaction: TransactionData) -> int:
        """
        Create transaction directly.
        
        Simple delegation to repository.
        For testing or special cases - normally use buy_stock() or sell_stock().
        
        Args:
            transaction: TransactionData instance
        
        Returns:
            Transaction ID
        """
        return self.transaction_repo.add(transaction)
    
    def get_transaction(self, transaction_id: int) -> TransactionData | None:
        return self.transaction_repo.get_by_id(transaction_id)
    
    
    def get_all_transactions(self) -> list[TransactionData]:
        return self.transaction_repo.get_all()
    
    def update_transaction(self, transaction: TransactionData) -> None:
        self.transaction_repo.update(transaction)
        
    
    def delete_transaction(self, transaction_id) -> None:
        self.stock_repo.delete(transaction_id)
    
    
    def get_portfolio_transactions(self, portfolio_id: int) -> list[TransactionData]:
        """Get all transactions for a portfolio"""
        return self.transaction_repo.get_by_portfolio(portfolio_id)
    
    def get_stock_transactions(self, stock_id: int) -> list[TransactionData]:
        """Get all the transactions for a stock"""
        return self.transaction_repo.get_by_stock(stock_id)
    
    
    def get_portfolio_stock_transactions(self, portfolio_id: int, stock_id: int) -> list[TransactionData]:
        """Get all the transaction for a stock in a portfolio"""
        return self.transaction_repo.get_by_portfolio_and_stock(portfolio_id, stock_id)
    
         
    # ==========================================
    # BUSINESS LOGIC - USER WORKFLOW 
    # ==========================================
    
    def buy_stock(
        self,
        portfolio_id: int,
        ticker: str,
        quantity: float,
        price: float,
        fee: float = 0.0
        ) -> int:
        """
        Buy stock - orchestrate complete purchase workflow
        
        Steps:
        1. Validate inputs
        2. Check if portfolio exists
        3. Get or create stock (fetch yfinance if needed)
        4. Create BUY transaction
        5. Holdings auto-update via VIEW
        
        Args:
            portfolio_id: Target portfolio
            ticker: Stock ticker (e.g., 'AAPL')
            quantity: Number of shares
            price: Price per share
            fee: Transaction fee
        
        Returns:
            Transaction ID
        
        Raises:
            ValueError: Invalid inputs or stock not found
        """
        
        # 1. Validate 
        if quantity <=0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")
        if fee < 0:
            raise ValueError("Fee cannot be negative")
        
        #2. Verify portfolio exists
        portfolio = self.portfolio_repo.get_by_id(portfolio_id)
        if portfolio is None:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        #3. Get or create stock
        stock = self.stock_repo.get_by_ticker(ticker.upper())
        if not stock:
            #Fetch from yfinance and create
            stock_data = self._fetch_stock_from_yfinance(ticker)
            stock_id = self.stock_repo.add(stock_data)
        else:
            stock_id = stock.id
        
        # 4. Create BUY transaction
        transaction = TransactionData(
            portfolio_id = portfolio_id,
            stock_id=stock_id,
            type='BUY',
            quantity=quantity,
            price=price,
            fee=fee,
            transaction_date=dt.datetime.now()
        )
        
        return self.transaction_repo.add(transaction)
    
    
    def sell_stock(
        self,
        portfolio_id: int,
        ticker: str,
        quantity: float,
        price: float,
        fee: float = 0.0
        ) -> int:
        """
        Sell stock - orchestrate complete purchase workflow
        
        Validates:
        - Stock exists in DB
        - Holding exists in DB
        - Sufficient quantity to sell
        
        Args:
            portfolio_id: Target portfolio
            ticker: Stock ticker (e.g., 'AAPL')
            quantity: Number of shares
            price: Price per share
            fee: Transaction fee
        
        Returns:
            Transaction ID
        
        Raises:
            ValueError: Validation failure
        """
        
        # 1. Validate 
        if quantity <=0:
            raise ValueError("Quantity must be positive")
        if price <= 0:
            raise ValueError("Price must be positive")
        if fee < 0:
            raise ValueError("Fee cannot be negative")
        
        # 2. Get stock (Must exist for SELL)
        stock = self.stock_repo.get_by_ticker(ticker.upper())
        if not stock:
            raise ValueError(f"Stock {ticker} not found in database")
        
        
        # 3. Verify if holding exists and has enough quantity
        holding = self.holding_repo.get_by_id(portfolio_id, stock.id)
        if not holding:
            raise ValueError(f"No holding for {ticker} in portfolio {portfolio_id}")
        
        if holding.total_shares < quantity:
            raise ValueError(
                f"Insufficient shares. "
                f"Have {holding.total_shares}, trying to sell {quantity}"
            )
        
        # 4. Create SELL transaction
        transaction = TransactionData(
            portfolio_id = portfolio_id,
            stock_id=stock.id,
            type='SELL',
            quantity=quantity,
            price=price,
            fee=fee,
            transaction_date=dt.datetime.now()
        )
        
        return self.transaction_repo.add(transaction)
    # ==========================================
    # PRIVATE HELPER
    # ==========================================
        
    def _fetch_stock_from_yfinance(self, ticker: str) -> StockData:
        """
        Fetch stock from yfinance and create StockData.
        
        Private helper method.
        
        Args:
            ticker: Stock ticker
        
        Returns:
            StockData instance
        
        Raises:
            ValueError: If stock not found or yfinance error
        """
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            #Validate stock existance
            if not info or 'symbol' not in info:
                raise ValueError(f"Stock {ticker} not found on yfinance")
            
            #Use mapper function
            return map_yfinance_to_stock(ticker, info)
        
        except ValueError:
            #Re raise validation errors
            raise
        except Exception as e:
            #Wrap other errors
            raise ValueError(f"Failed to fetch {ticker} from yfinance: {str(e)}")
        
            
        
        
    
        

    
    
