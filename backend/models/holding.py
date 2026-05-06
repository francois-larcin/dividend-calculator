from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class HoldingData:
    portfolio_id: int
    stock_id: int 
    ticker: str
    company_name: str
    total_shares: float
    avg_price: float
    total_invested: float # with fees (comes from DB)
    currency: str = 'EUR'
    date_added: dt.datetime | None = None
    
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
    def cost_without_fees(self) -> float:
        """Returns therorical cost as if there were no transaction fee"""
        return self.total_shares * self.avg_price
    
    
    @property
    def total_fees(self) -> float:
        """Calculate total transaction fee paid"""
    
        return self.total_invested - self.cost_without_fees
    
    
    @property 
    def fee_percentage(self) -> float:
        """Calculate implied fee percentage"""
        expected_cost = self.total_shares * self.avg_price
        implied_fee = self.total_invested - expected_cost
        
        if expected_cost == 0:
            return 0.0
        
        return (implied_fee / expected_cost) * 100
    
    # ==========================================
    # VALIDATIONS
    # ==========================================
    @property
    def has_reasonable_fees(self) -> bool:
        """Check if fees are within reasonable range (< 5%)"""
        return 0 <= self.fee_percentage <= 5.0
    
    
    # ==========================================
    # CALCULATIONS WITH CURRENT PRICE
    # ==========================================
    
    
    def current_value(self, price: float) -> float:
        """Calculate current market value at given price"""
        return self.total_shares * price
    
    
    def unrealized_gain(self, price: float) -> float:
        """Calculate unrealized P/L (include fees)"""
        return self.current_value(price) - self.total_invested
    
    def gain_percentage(self, price: float) -> float:
        """Gain percentage relative to total invested"""
        if self.total_invested == 0:
            return 0.0
        
        return (self.unrealized_gain(price) / self.total_invested) * 100 


######################################      TESTS      ######################################

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
        total_invested=1505.0,  # 10 × 150 + 5€ de frais
        date_added=dt.datetime(2024, 1, 15)
    )
    
    print(f"Holding: {holding}")
    print(f"\nDétail des coûts:")
    print(f"  Shares: {holding.total_shares}")
    print(f"  Prix moyen: {holding.avg_price:.2f}€")
    print(f"  Coût sans frais: {holding.cost_without_fees:.2f}€")
    print(f"  Total investi (AVEC frais): {holding.total_invested:.2f}€")
    print(f"  Frais totaux: {holding.total_fees:.2f}€")
    print(f"  Frais en %: {holding.fee_percentage:.2f}%")
    print(f"  Frais raisonnables: {holding.has_reasonable_fees}")
  
    
    # Test avec prix actuel
    current_price = 170.0
    print(f"\nAvec prix actuel = {current_price}€:")
    print(f"  Valeur actuelle: {holding.current_value(current_price):.2f}€")
    print(f"  Gain latent: {holding.unrealized_gain(current_price):.2f}€")
    print(f"  Gain %: {holding.gain_percentage(current_price):.2f}%")