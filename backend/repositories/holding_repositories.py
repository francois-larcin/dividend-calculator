from backend.database.connection import DatabaseConnection
from backend.models.holding import HoldingData


class HoldingRepository:
    
    def __init__(self, db_config: dict):
        """
        Initialize repository with database config.
        
        Args:
            db_config: Dict with 'host', 'database', 'user', 'password'
        """
        self.db_config = db_config
        
    # ==========================================
    # NO CRUD (it's a VIEW, not a TABLE)
    # ==========================================
    
    
    # ==========================================
    # SPECIFIC METHODS
    # ==========================================
    
    def get_by_portfolio(self, portfolio_id: int) -> list[HoldingData]:
        """
        Get all the holdings for a portfolio searched by its id
        
        Args:
            portfolio_id: the portfolio id to find
            
        Returns:
            list[HoldingData] if found, None otherwhise
        """
        
        query = """
            SELECT portfolio_id, stock_id, ticker, company_name, 
            currency, avg_price, date_added, total_invested
            FROM current_holdings
            WHERE portfolio_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id, ))
            rows = cursor.fetchall()
            
            return [
                HoldingData(
                portfolio_id=row[0],
                stock_id=row[1],
                ticker=row[2],
                company_name=row[3],
                currency=row[4],
                avg_price=row[5],
                date_added=row[6],
                total_invested=row[7]
                )
            for row in rows   
            ]
            
    def get_by_id(self, portfolio_id: int, stock_id: int) -> HoldingData | None:
        """Get a specific holding (composite key).
        
        Args:
            portfolio_id: the portfolio id to find
            stock_id: the stock id to find
            
            Together, the create the composite key
            
        Returns:
            list[HoldingData] if found, None otherwhise
        """
        
        query = """
            SELECT portfolio_id, stock_id, ticker, company_name, 
            currency, avg_price, date_added, total_invested
            FROM current_holdings
            WHERE portfolio_id = %s AND stock_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id, stock_id, ))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return HoldingData(
                portfolio_id=row[0],
                stock_id=row[1],
                ticker=row[2],
                company_name=row[3],
                currency=row[4],
                avg_price=row[5],
                date_added=row[6],
                total_invested=row[7]
                )
            
    
    