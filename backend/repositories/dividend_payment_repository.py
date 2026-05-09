from backend.database.connection import DatabaseConnection
from backend.models.dividend_payment import DividendPaymentData
import datetime as dt

class DividendPaymentRepository:
    
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
    
    def add(self, div_payment: DividendPaymentData) -> int:
        """Insert a new dividend payment in the transactions TABLE.
        
        Args:
            div_payment: DividendPaymentData instance to insert
        
        Returns:
            The ID of the newly created div_payment"""
            
        query = """
            INSERT INTO dividend_payments (
                portfolio_id, stock_id, amount_per_share, total_amount, paid_at, ex_dividend_date
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                div_payment.portfolio_id,
                div_payment.stock_id,
                div_payment.amount_per_share,
                div_payment.total_amount,
                div_payment.paid_at or dt.datetime.now(),
                div_payment.ex_dividend_date or dt.datetime.now()
            ))
            
            new_id = cursor.fetchone()[0]
            return new_id

    # ==========================================
    # READ
    # ==========================================
    
    def get_by_id(self, div_payment_id: int) -> DividendPaymentData | None:
        """
        Get a div payment by its ID.
        
        Args:
            div_payment_id: The transaction ID to find
        
        Returns:
            DividendPaymentData if found, None otherwise
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, amount_per_share, total_amount, paid_at, ex_dividend_date
            FROM dividend_payments
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (div_payment_id, ))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return DividendPaymentData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                amount_per_share=row[3],
                total_amount=row[4],
                paid_at=row[5],
                ex_dividend_date=row[6]
            )
    
    def get_all(self) -> list[DividendPaymentData]:
        """
        Get all div payments from DB
        
        Returns:
            List of all DividendPaymentData instances
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, amount_per_share, total_amount, paid_at, ex_dividend_date
            FROM dividend_payments 
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                DividendPaymentData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                amount_per_share=row[3],
                total_amount=row[4],
                paid_at=row[5],
                ex_dividend_date=row[6]
            )
            for row in rows
            ]
            
    # ==========================================
    # UPDATE
    # ==========================================
    
    def update(self, div_payment: DividendPaymentData) -> None:
        """
        Update a div payment in the database.
        
        Args:
            div_payment: DividendPaymentData instance with updated values
        """
        
        query = """
            UPDATE dividend_payments
            SET portfolio_id = %s,
            stock_id = %s,
            amount_per_share = %s,
            total_amount = %s,
            paid_at = %s,
            ex_dividend_date = %s
            WHERE id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                div_payment.portfolio_id,
                div_payment.stock_id,
                div_payment.amount_per_share,
                div_payment.total_amount,
                div_payment.paid_at or dt.datetime.now(),
                div_payment.ex_dividend_date or dt.datetime.now(),
                div_payment.id,
            ))
            
    # ==========================================
    # DELETE
    # ==========================================
    
    def delete(self, div_payment_id: int) -> None:
        """
        Delete a div payment from the DB
        
        Args:
            div_payment_id: The div payment ID to delete
        """
        
        query = "DELETE FROM dividend_payments WHERE id = %s"
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (div_payment_id,))
    
    
    # ==========================================
    # SPECIFIC METHODS
    # ==========================================
    
    def get_by_portfolio(self, portfolio_id: int) -> list[DividendPaymentData]:
        """
        Get all the div payments for a portfolio searched by its id
        
        Args:
            portfolio_id: the portfolio id to find
            
        Returns:
            list[DividendPaymentData] if found, None otherwhise
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, amount_per_share, total_amount, paid_at, ex_dividend_date
            FROM dividend_payments 
            WHERE portfolio_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id, ))
            rows = cursor.fetchall()
            
            return [
                DividendPaymentData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                amount_per_share=row[3],
                total_amount=row[4],
                paid_at=row[5],
                ex_dividend_date=row[6]
                )
            for row in rows   
            ]
           
    def get_by_date_range(self, start_date: dt.datetime, end_date: dt.datetime) -> list[DividendPaymentData]:
        """
        Get all the div payments for a period of time
            
        Returns:
            List of DividendPaymentData received between start_date and end_date
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, amount_per_share, total_amount, paid_at, ex_dividend_date
            FROM dividend_payments 
            WHERE paid_at BETWEEN %s AND %s
            ORDER BY paid_at DESC
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (start_date, end_date, ))
            rows = cursor.fetchall()
            
            return [
                DividendPaymentData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                amount_per_share=row[3],
                total_amount=row[4],
                paid_at=row[5],
                ex_dividend_date=row[6]
                )
            for row in rows   
            ]
        
    def get_by_stock(self, stock_id: int) -> list[DividendPaymentData]:
        """
        Get all the div payments for one specific stock
        
        Args:
            stock_id : the id from the stock
            
        Returns:
            List of DividendPaymentData with that stock_id
        """
        
        query = """
            SELECT id, portfolio_id, stock_id, amount_per_share, total_amount, paid_at, ex_dividend_date
            FROM dividend_payments 
            WHERE stock_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (stock_id, ))
            rows = cursor.fetchall()
            
            return [
                DividendPaymentData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                amount_per_share=row[3],
                total_amount=row[4],
                paid_at=row[5],
                ex_dividend_date=row[6]
                )
            for row in rows   
            ]
            
            
    def get_by_portfolio_and_stock(self, portfolio_id: int, stock_id: int) -> list[DividendPaymentData]:
        """
        Get all the div payments from one stock in one portfolio
        
        Args:
            portfolio_id : the id of the portfolio
            stock_id: the id of the stock
            
        Returns:
            List od DividentData with that portfolio_id and stock_id"""
            
        query = """
            SELECT id, portfolio_id, stock_id, amount_per_share, total_amount, paid_at, ex_dividend_date
            FROM dividend_payments 
            WHERE portfolio_id = %s AND stock_id = %s
        """
        
        with DatabaseConnection(self.db_config) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (portfolio_id, stock_id, ))
            rows = cursor.fetchall()
            
            return [
                DividendPaymentData(
                id=row[0],
                portfolio_id=row[1],
                stock_id=row[2],
                amount_per_share=row[3],
                total_amount=row[4],
                paid_at=row[5],
                ex_dividend_date=row[6]
                )
            for row in rows   
            ]
            