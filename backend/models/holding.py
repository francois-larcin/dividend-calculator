from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class HoldingData:
    stock_id: int 
    ticker: str
    company_name: str
    total_shares: float
    avg_price: float
    currency: str = 'EUR'
    date_added: dt.datetime | None = None
    portfolio_id: int | None = None
    
    def __repr__(self) -> str:
        """Dev-friendly representation"""
        return f"HoldingData({self.ticker}, {self.total_shares} shares)"
    
    
    def __str__(self) -> str:
        """User-friendly representation"""
        return f"{self.ticker}: {self.total_shares:.2f} shares at {self.avg_price:.2f}"
    
    # ==========================================
    # COST CALCULATIONS
    # ==========================================
     
    @property
    def total_invested(self) -> float:
        """Returns the total invested with current positions"""
        return float(self.total_shares * self.avg_price)
        
    
    # ==========================================
    # CALCULATIONS WITH CURRENT PRICE
    # ==========================================
    
    
    def current_value(self, price: float) -> float:
        """Calculate current market value at given price"""
        if not price:
            return 0.0
        
        return float(self.total_shares * price)
    
    
    def unrealized_gain(self, price: float) -> float:
        """Calculate unrealized P/L (include fees) based on current position cost"""
        if not price:
            return 0.0
    
        return float(self.current_value(price) - self.total_invested)
    
    
    def gain_percentage(self, price: float) -> float:
        """Gain percentage relative to current position cost"""
        
        if self.total_invested == 0 or not price:
            return 0.0
        
        return (self.unrealized_gain(price) / self.total_invested) * 100 
    
    
###################################      TESTS      ###################################

if __name__ == "__main__":
    print("=== Tests HoldingData - Calculs de frais ===\n")
    
    # Exemple réaliste
    holding = HoldingData(
        portfolio_id=1,
        stock_id=1,
        ticker='AAPL',
        company_name='Apple Inc.',
        total_shares=10.0,
        avg_price=150.0,
        date_added=dt.datetime(2024, 1, 15)
    )
    
    print(f"Holding: {holding}")
    print(f"\nDétail des coûts:")
    print(f"  Shares: {holding.total_shares}")
    print(f"  Prix moyen: {holding.avg_price:.2f}€")
    
    # Test avec prix actuel
    current_price = 170.0
    print(f"\nAvec prix actuel = {current_price}€:")
    print(f"  Valeur actuelle: {holding.current_value(current_price):.2f}€")
    print(f"  Gain latent: {holding.unrealized_gain(current_price):.2f}€")
    print(f"  Gain %: {holding.gain_percentage(current_price):.2f}%")