"""Checker la doc Python pour voir les bonnes pratiques pour module ou package"""

def calculate_dividend_yield(annual_dividend: float, price: float) -> float:
    """Calculate dividend yield percentage"""
    if annual_dividend < 0:
        raise ValueError("Annual dividend cannot be negative")
    if price <= 0: 
        raise ValueError("Price must be greater than 0")
    return (annual_dividend / price) * 100


def calculate_total_return(dividends_received: float, capital_gain: float, initial_investment: float) -> float:
    """Calculate total return percentage from dividends and capital gains"""
    if initial_investment <= 0:
        raise ValueError("Initial investment must be greater than 0")
    if dividends_received <= 0:
        raise ValueError("Dividends received cannot be negative")
    return (dividends_received + capital_gain)/initial_investment * 100

#print(calculate_total_return(50, 50, 1000))


def project_futures_dividends(current_dividend: float, growth_rate: float, years: int) -> list[float]:
    """Project future dividends with annual growth."""
    
    if years < 1:
        raise ValueError("Years must be at least 1")
    
    div_projection = []
    
    for _ in range(years):
        current_dividend *= (1 + growth_rate)
        div_projection.append(current_dividend)

    return div_projection

#print(project_futures_dividends(50, 0.03, 10))


list_dividends_2 = [1.00, 2.00]
list_dividends = [1.00, 1.10, 1.09, 1.12]

def annualized_growth_rate(dividend_history: list[float]) -> float:
    """Calculates CAGR (Compound Annual Growth Rate) from a list of dividends"""
    if len(dividend_history) < 2:
        raise ValueError("Need at least 2 data points to calculate growth rate")
    
    initial_div = dividend_history[0]
    last_div = dividend_history[-1]
    year_nb = len(dividend_history) - 1
    carg = ((last_div / initial_div) ** (1 / year_nb) - 1)
    return carg

#print(annualized_growth_rate(list_dividends))


# Dans votre if __name__ == "__main__":
print("\n=== Tests annualized_growth_rate ===")

# Test 1 : Croissance réelle d'Apple
result = annualized_growth_rate([0.80, 0.85, 0.90, 0.95, 1.00])
print(f"Test 1: {result:.4f} (attendu: ~0.0574)")

# Test 2 : Croissance zéro
result = annualized_growth_rate([1.0, 1.0, 1.0])
print(f"Test 2: {result:.4f} (attendu: 0.0000)")

# Test 3 : Décroissance
result = annualized_growth_rate([1.00, 0.95, 0.90])
print(f"Test 3: {result:.4f} (attendu: -0.0513)")