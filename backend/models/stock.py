from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class StockData:
    id: int
    ticker: str
    company_name: str
    
    sector: str | None = None
    industry: str | None = None 
    dividend_frequency: int | None = None 
    last_update_at: dt.datetime | None = None
    
    currency: str = 'EUR'
    
    def __repr__(self) -> str:
        """Dev-friendly representation"""
        return f"StockData(id:{self.id}, ticker:{self.ticker})"
    
    
    def __str__(self) -> str:
        """User-friendly representation"""
        parts = [f"{self.company_name} ({self.ticker})"]
        if self.sector:
            parts.append(f"- {self.sector}")
        return " ".join(parts)
    
    @property
    def is_quarterly(self) -> bool:
        """Check if dividend is paid quarterly"""
        return self.dividend_frequency == 4
    
    @property
    def is_annual(self) -> bool:
        """Checks if dividend is paid annually"""
        return self.dividend_frequency == 1
    
    @property
    def is_biannual(self) -> bool:
        """Checks if dividend is paid half-yearly"""
        return self.dividend_frequency == 2
    
######################################      TESTS      ######################################

if __name__ == "__main__":
    print("=== Tests StockData ===\n")
    
    # Test 1: Stock complet
    stock1 = StockData(
        id=1,
        ticker='AAPL',
        company_name='Apple Inc.',
        sector='Technology',
        industry='Consumer Electronics',
        currency='USD',
        dividend_frequency=4,
        last_update_at=dt.datetime.now()
    )
    
    print(f"Test 1 - Stock complet:")
    print(f"  str(): {stock1}")
    print(f"  repr(): {repr(stock1)}")
    print(f"  Quarterly? {stock1.is_quarterly}")
    print(f"  Yearly? {stock1.is_annual}")
    print(f"  Half-yearly? {stock1.is_biannual}")
    
    # Test 2: Stock minimal
    stock2 = StockData(
        id=2,
        ticker='MSFT',
        company_name='Microsoft Corporation'
    )
    
    print(f"\nTest 2 - Stock minimal:")
    print(f"  str(): {stock2}")
    print(f"  Currency par défaut: {stock2.currency}")
    
    # Test 3: Immutabilité (doit échouer)
    print(f"\nTest 3 - Test immutabilité:")
    try:
        stock1.ticker = 'GOOG'
        print("  ❌ ERREUR: La modification a réussi (ne devrait pas !)")
    except Exception as e:
        print(f"  ✅ Immutable confirmé: {type(e).__name__}")  
    
    
    
    
    
    
