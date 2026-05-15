from backend.database.connection import DatabaseConnection
from backend.models.stock import StockData
import datetime as dt

class StockRepository:
     
    def __init__(self, db_config: dict):
        """
        Initialize repository with database config.
        
        Args:
            db_config: Dict with 'host', 'database', 'user', 'password'
        """
        self.db_config = db_config
    
    
    # ==========================================
    # CREATE
    # ==========================================
    
    def add(self, stock: StockData) -> int:
        """Insert a new stock into the database.
        
        Args:
            stock: StockData instance to insert
        
        Returns:
            The ID of the newly created stock"""
            
        query = """
            INSERT INTO stocks (
                ticker, company_name, sector, industry, currency, last_update_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                stock.ticker,
                stock.company_name,
                stock.sector,
                stock.industry,
                stock.currency,
                stock.last_update_at or dt.datetime.now()
            ))
            
            new_id = cursor.fetchone()[0]
            return new_id
            
    # ==========================================
    # READ
    # ==========================================
    
    def get_by_id(self, stock_id: int) -> StockData | None:
        """
        Get a stock by its ID.
        
        Args:
            stock_id: The stock ID to find
        
        Returns:
            StockData if found, None otherwise
        """
        
        query = """
            SELECT id, ticker, company_name, sector, industry, 
                   currency, last_update_at
            FROM stocks
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (stock_id, ))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return StockData(
                id=row[0],
                ticker=row[1],
                company_name=row[2],
                sector=row[3],
                industry=row[4],
                currency=row[5],
                last_update_at=row[6]
            )
    
    
    def get_all(self) -> list[StockData]:
        """
        Get all stocks from DB
        
        Returns:
            List of all StockData instances
        """
        
        query = """
            SELECT id, ticker, company_name, sector, industry, currency, last_update_at
            FROM stocks
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                StockData(
                id=row[0],
                ticker=row[1],
                company_name=row[2],
                sector=row[3],
                industry=row[4],
                currency=row[5],
                last_update_at=row[6]
            )
            for row in rows
            ]
        
    # ==========================================
    # UPDATE
    # ==========================================
    
    def update(self, stock: StockData) -> None:
        """
        Update a stock in the database.
        
        Args:
            stock: StockData instance with updated values
        """
        query = """
            UPDATE stocks
            SET ticker = %s,
            company_name = %s,
            sector = %s,
            industry = %s,
            currency = %s,
            last_update_at = %s
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                stock.ticker,
                stock.company_name,
                stock.sector,
                stock.industry,
                stock.currency,
                stock.last_update_at or dt.datetime.now(),
                stock.id
            ))
        
    # ==========================================
    # DELETE
    # ==========================================
    
    def delete(self, stock_id: int) -> None:
        """
        Delete a stock from the DB
        
        Args:
            stock_id: The stock ID to delete
        """
        
        query = "DELETE FROM stocks WHERE id = %s"
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (stock_id, ))
            
    # ==========================================
    # SPECIFIC METHODS
    # ==========================================
    
    def search_by_sector(self, sector: str) -> list[StockData]:
        """
        Search stocks by sector.
        
        Args:
            sector: The sector name
            
        Returns:
            List of StockData in that sector
            
        """

        query= """
        
            SELECT id, ticker, company_name, sector, industry, currency, last_update_at
            FROM stocks
            WHERE sector = %s
            
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (sector, ))
            rows = cursor.fetchall()
            
            return [
                StockData(
                id=row[0],
                ticker=row[1],
                company_name=row[2],
                sector=row[3],
                industry=row[4],
                currency=row[5],
                last_update_at=row[6]
                )
            for row in rows
            ]
                
    
    def get_by_ticker(self, ticker: str) -> StockData | None:
        """
        Get a stock by its ticker.
        
        Args:
            ticker: the company ticker to find
        
        Returns:
            StockData if found, None otherwise
        """
        
        query = """
            SELECT id, ticker, company_name, sector, industry, 
                   currency, last_update_at
            FROM stocks
            WHERE ticker = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (ticker, ))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return StockData(
                id=row[0],
                ticker=row[1],
                company_name=row[2],
                sector=row[3],
                industry=row[4],
                currency=row[5],
                last_update_at=row[6]
            )
    