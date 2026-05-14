from dataclasses import dataclass
import datetime as dt


@dataclass()
class DividendPaymentData:
    portfolio_id: int
    stock_id: int 
    amount_per_share: float
    total_amount: float
    paid_at: dt.datetime | None = None
    ex_dividend_date: dt.datetime | None = None
    id: int | None = None
    
    def __repr__(self) -> str:
        """Dev-friendly representation"""
        return f"DividendPaymentData(id={self.id}, {self.total_amount} in total)"
    
    def __str__(self) -> str:
        """User-friendly representation"""
        return f"{self.amount_per_share} per share for a total of {self.total_amount} paid at {self.ex_dividend_date}"
    
    
