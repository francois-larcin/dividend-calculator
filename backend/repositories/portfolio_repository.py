from backend.database.connection import DatabaseConnection
from backend.models.portfolio import PortfolioData

import datetime as dt


class PortfolioRepository:
    
    def __init__(self, db_config: dict):
        """
        Initialize repo with database config.
        
        Args:
            db_config: Dict with 'host', 'database', 'user', 'password'
        """
        
        self.db_config = db_config
    
    # ==========================================
    # CREATE
    # ==========================================
    
    def add(self, portfolio: PortfolioData) -> int:
        """Insert a new transaction in the transactions TABLE.
        
        Args:
            div_payment: PortfolioData instance to insert
        
        Returns:
            The ID of the newly created portfolio"""
            
        query = """
            INSERT INTO portfolios (
                user_id, name, currency, created_at
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                portfolio.user_id,
                portfolio.name,
                portfolio.currency,
                portfolio.created_at or dt.datetime.now()
            ))
            
            new_id = cursor.fetchone()[0]
            return new_id 

    # ==========================================
    # READ
    # ==========================================
    
    def get_by_id(self, portfolio_id: int) -> PortfolioData | None:
        """
        Get a portfolio by its ID.
        
        Args:
            portfolio_id: The portfolio ID to find
        
        Returns:
            PortfolioData if found, None otherwise
        """
        
        query = """
            SELECT id, user_id, name, currency, created_at
            FROM portfolios
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id, ))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return PortfolioData(
                id=row[0],
                user_id=row[1],
                name=row[2],
                currency=row[3],
                created_at=row[4]
            )
            
    def get_all(self) -> list[PortfolioData]:
        """
        Get all portfolios from DB
        
        Returns:
            List of all PortfolioData instances
        """
        
        query = """
            SELECT id, user_id, name, currency, created_at
            FROM portfolios
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                PortfolioData(
                id=row[0],
                user_id=row[1],
                name=row[2],
                currency=row[3],
                created_at=row[4]
            )
            for row in rows
            ]
    
    # ==========================================
    # UPDATE
    # ==========================================
    
    def update(self, portfolio: PortfolioData) -> None:
        """
        Update a portfolio in the database.
        
        Args:
            portfolio: PortfolioData instance with updated values
        """
        
        query = """
            UPDATE portfolios
            SET user_id = %s,
            name = %s,
            currency = %s,
            created_at = %s
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                portfolio.user_id,
                portfolio.name,
                portfolio.currency,
                portfolio.created_at or dt.datetime.now(),
                portfolio.id
            ))
            
    # ==========================================
    # DELETE
    # ==========================================
    
    def delete(self, portfolio_id: int) -> None:
        """
        Delete a portfolio from the DB
        
        Args:
            portfolio_id: The portfolio ID to delete
        """
        
        query = "DELETE FROM portfolios WHERE id = %s"
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id,))
            
    # ==========================================
    # SPECIFIC METHODS
    # ==========================================
    
    def get_by_user(self, user_id: int) -> list[PortfolioData]:
        """
        Get a portfolio by it's user id.
        
        Args:
            user_id: The user ID to find
        
        Returns:
            DividendPaymentData if found, None otherwise
        """
        
        query = """
            SELECT id, user_id, name, currency, created_at
            FROM portfolios
            WHERE user_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user_id, ))
            rows = cursor.fetchall()
            
            return [
                PortfolioData(
                id=row[0],
                user_id=row[1],
                name=row[2],
                currency=row[3],
                created_at=row[4]
            )
            for row in rows
            ]
        