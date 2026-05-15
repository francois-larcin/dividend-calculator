

from backend.database.connection import DatabaseConnection
from backend.models.transaction import TransactionData
import datetime as dt


class TransactionRepository:
    
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
    
    def add(self, transaction: TransactionData) -> int:
        """Insert a new transaction in the transactions TABLE.
        
        Args:
            transaction: TransactionData instance to insert
        
        Returns:
            The ID of the newly created transaction"""
            
        query = """
            INSERT INTO transactions (
                portfolio_id, stock_id, type, quantity, price, fee, transaction_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                transaction.portfolio_id,
                transaction.stock_id,
                transaction.type,
                transaction.quantity,
                transaction.price,
                transaction.fee,
                transaction.transaction_date or dt.datetime.now()
            ))
            
            new_id = cursor.fetchone()[0]
            return new_id
    
    # ==========================================
    # READ
    # ==========================================
    
    def get_by_id(self, t_id: int) -> TransactionData | None:
        """
        Get a transaction by its ID.
        
        Args:
            t_id: The transaction ID to find
        
        Returns:
            transactionData if found, None otherwise
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, type, quantity, price, fee, transaction_date
            FROM transactions 
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (t_id, ))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return TransactionData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                type=row[3],
                quantity=row[4],
                price=row[5],
                fee=row[6],
                transaction_date=row[7]
            )
        
        
    def get_all(self) -> list[TransactionData]:
        """
        Get all transactions from DB
        
        Returns:
            List of all TransactionData instances
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, type, quantity, price, fee, transaction_date
            FROM transactions 
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                TransactionData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                type=row[3],
                quantity=row[4],
                price=row[5],
                fee=row[6],
                transaction_date=row[7]
            )
            for row in rows
            ]
    
    # ==========================================
    # UPDATE
    # ==========================================
    
    def update(self, transaction: TransactionData) -> None:
        """
        Update a transaction in the database.
        
        Args:
            transaction: transactionData instance with updated values
        """
        query = """
            UPDATE transactions
            SET portfolio_id = %s,
            stock_id = %s,
            type = %s,
            quantity = %s,
            price = %s,
            fee = %s,
            transaction_date = %s
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                transaction.portfolio_id,
                transaction.stock_id,
                transaction.type,
                transaction.quantity,
                transaction.price,
                transaction.fee,
                transaction.transaction_date or dt.datetime.now(),
                transaction.id,
            ))
        
    # ==========================================
    # DELETE
    # ==========================================
    
    def delete(self, t_id: int) -> None:
        """
        Delete a transaction from the DB
        
        Args:
            t_id: The stock ID to delete
        """
        
        query = "DELETE FROM transactions WHERE id = %s"
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (t_id, ))
            
    # ==========================================
    # SPECIFIC METHODS
    # ==========================================
    
    def get_by_portfolio(self, portfolio_id: int) -> list[TransactionData]:
        """
        Get all the transcation for a portfolio searched by its id
        
        Args:
            portfolio_id: the portfolio id to find
            
        Returns:
            list[TransactionData] if found, None otherwhise
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, type, quantity, price, fee, transaction_date
            FROM transactions
            WHERE portfolio_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id, ))
            rows = cursor.fetchall()
            
            return [
                TransactionData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                type=row[3],
                quantity=row[4],
                price=row[5],
                fee=row[6],
                transaction_date=row[7]
                )
            for row in rows   
            ]
        
    def get_by_stock(self, stock_id: int) -> list[TransactionData]:
        """
        Get all the transactions for one specific stock
        
        Args:
            stock_id : the id from the stock
            
        Returns:
            List of TransactionData with that stock_id
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, type, quantity, price, fee, transaction_date
            FROM transactions
            WHERE stock_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (stock_id, ))
            rows = cursor.fetchall()
            
            return [
                TransactionData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                type=row[3],
                quantity=row[4],
                price=row[5],
                fee=row[6],
                transaction_date=row[7]
                )
            for row in rows   
            ]
            
            
    def get_by_portfolio_and_stock(self, portfolio_id: int, stock_id: int) -> list[TransactionData]:
        """
        Get all the transactions for one specific stock in a portfolio
        
        Args:
            stock_id : the id from the stock
            portfolio_id : the portfolio id to find
            
        Returns:
            List of TransactionData with that stock_id in that portfolio_id
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, type, quantity, price, fee, transaction_date
            FROM transactions
            WHERE portfolio_id = %s AND stock_id = %s
            ORDER BY transaction_date DESC
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id, stock_id, ))
            rows = cursor.fetchall()
            
            return [
                TransactionData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                type=row[3],
                quantity=row[4],
                price=row[5],
                fee=row[6],
                transaction_date=row[7]
                )
            for row in rows   
            ]
        
        
        
        