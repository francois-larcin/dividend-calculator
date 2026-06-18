from dataclasses import dataclass, field
import datetime as dt

from backend.models.holding import HoldingData


@dataclass()
class PortfolioData:
    user_id: int
    name: str
    
    currency: str = 'EUR'
    created_at: dt.datetime | None = None
    id: int | None = None
    
    #Each instance has its own empty list
    holdings: list[HoldingData] = field(default_factory=list) 


    def __repr__(self) -> str:
        """Dev-friendly representation"""
        return f"PortfolioData({self.id}, {self.name}, {len(self.holdings)})"

    def __str__(self) -> str:
        """User-friendly representation"""
        return f"{self.name} ({self.currency}) - {len(self.holdings)} positions"
    
    # ==========================================
    # SPECIAL METHODS
    # ==========================================
    
    def __len__(self) -> int:
        return len(self.holdings)
    
    
    def __iter__(self):
        return iter(self.holdings)
    
    # ==========================================
    # USEFUL METHODS
    # ==========================================
    
    def find_holding_by_ticker(self, ticker: str) -> HoldingData | None:
        """Find a holding via its ticker in THIS portfolio's list"""
        return next((h for h in self.holdings if h.ticker == ticker), None)
        
        
    def current_value(self, current_prices: dict[int: float]) -> float:
        """Calculate current portfolio value at given with market prices"""
        
        return float(sum(
            #current_value = current market value for all shares from 1 stock
            h.current_value(current_prices.get(h.stock_id, 0))
            for h in self.holdings
        ))
        
        
    def total_invested(self) -> float:
        """Calculate total invested across all holdings"""
        return float(sum(h.total_invested for h in self.holdings))
        
        
if __name__ == "__main__":
    print("=== Tests PortfolioData avec HoldingData réels ===\n")
    
    # ==========================================
    # Test 1 : Créer un portfolio vide
    # ==========================================
    
    portfolio = PortfolioData(
        id=1,
        user_id=1,
        name='Dividendes Mensuels',
        currency='EUR',
        created_at=dt.datetime(2024, 1, 1)
    )
    
    print(f"Test 1 - Portfolio vide:")
    print(f"  str(): {portfolio}")
    print(f"  repr(): {repr(portfolio)}")
    print(f"  len(): {len(portfolio)}")
    print(f"  Total investi: {portfolio.total_invested}$")
    
    # ==========================================
    # Test 2 : Ajouter un holding réel
    # ==========================================
    
    holding1 = HoldingData(
        portfolio_id=1,
        stock_id=34,
        ticker='VISTA',
        company_name='Vista Energy',
        total_shares=10.0,
        avg_price=50.0,
        total_invested=505.0,
        currency='USD',
        date_added=dt.datetime.now()
    )
    
    portfolio.add_holding(holding1)
    
    print(f"\nTest 2 - Après ajout de VISTA:")
    print(f"  {portfolio}")
    print(f"  len(): {len(portfolio)}")
    print(f"  Total investi: {portfolio.total_invested:.2f}$")
    
    # ==========================================
    # Test 3 : Ajouter plusieurs holdings
    # ==========================================
    
    holding2 = HoldingData(
        portfolio_id=1,
        stock_id=12,
        ticker='AAPL',
        company_name='Apple Inc.',
        total_shares=5.0,
        avg_price=150.0,
        total_invested=755.0,
        currency='USD',
        date_added=dt.datetime(2024, 2, 15)
    )
    
    holding3 = HoldingData(
        portfolio_id=1,
        stock_id=8,
        ticker='MC.PA',
        company_name='LVMH',
        total_shares=3.0,
        avg_price=750.0,
        total_invested=2255.0,
        currency='EUR',
        date_added=dt.datetime(2024, 3, 1)
    )
    
    portfolio.add_holding(holding2)
    portfolio.add_holding(holding3)
    
    print(f"\nTest 3 - Portfolio avec 3 holdings:")
    print(f"  {portfolio}")
    print(f"  Nombre de positions: {len(portfolio)}")
    print(f"  Total investi: {portfolio.total_invested:.2f}€")
    
    # ==========================================
    # Test 4 : Itération (__iter__)
    # ==========================================
    
    print(f"\nTest 4 - Itération sur les holdings:")
    for holding in portfolio:  # ← Use __iter__
        symbol = {'EUR': '€', 'USD': '$'}.get(holding.currency, '')
        print(f"  - {holding.ticker}: {holding.total_shares:.2f} shares "
              f"at {holding.avg_price:.2f}{symbol} "
              f"(total: {holding.total_invested:.2f}{symbol})")
    
    # ==========================================
    # Test 5 : Recherche par ticker
    # ==========================================
    
    print(f"\nTest 5 - Recherche par ticker:")
    apple = portfolio.find_holding_by_ticker('AAPL')
    if apple:
        print(f"  AAPL trouvé: {apple.total_shares} shares @ {apple.avg_price}$")
    
    vista = portfolio.find_holding_by_ticker('VISTA')
    if vista:
        print(f"  VISTA trouvé: {vista.total_shares} shares @ {vista.avg_price}$")
    
    not_found = portfolio.find_holding_by_ticker('MSFT')
    print(f"  MSFT trouvé: {not_found}")  # None
    
    # ==========================================
    # Test 6 : List comprehension (grâce à __iter__)
    # ==========================================
    
    print(f"\nTest 6 - List comprehensions:")
    
    # Tous les tickers
    tickers = [h.ticker for h in portfolio]
    print(f"  Tickers: {tickers}")
    
    # Actions US seulement
    us_stocks = [h.ticker for h in portfolio if h.currency == 'USD']
    print(f"  Actions US: {us_stocks}")
    
    # Actions EU seulement
    eu_stocks = [h.ticker for h in portfolio if h.currency == 'EUR']
    print(f"  Actions EU: {eu_stocks}")
    
    # ==========================================
    # Test 7 : Calculs avec les properties
    # ==========================================
    
    print(f"\nTest 7 - Calculs sur le portfolio:")
    print(f"  Total shares count: {portfolio.total_shares_count}")
    print(f"  Total investi: {portfolio.total_invested:.2f}€")
    
    # Calcul manuel pour vérifier
    manual_total = sum(h.total_invested for h in portfolio)
    print(f"  Vérification manuelle: {manual_total:.2f}€")
    print(f"  Match: {portfolio.total_invested == manual_total}")
    
    # ==========================================
    # Test 8 : Frais des holdings
    # ==========================================
    
    print(f"\nTest 8 - Analyse des frais:")
    for holding in portfolio:
        print(f"  {holding.ticker}:")
        print(f"    Coût sans frais: {holding.total_invested_without_fees:.2f}")
        print(f"    Frais totaux: {holding.total_fees:.2f}")
        print(f"    Frais %: {holding.fee_percentage:.2f}%")
        print(f"    Frais raisonnables: {holding.has_reasonable_fees}")







