from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class TransactionData:
    id: int
    portfolio_id: int
    stock_id: int
    type: str # BUY or SELL
    quantity: float
    price: float
    fee: float
    transaction_date: dt.datetime | None = None
    
    def __repr__(self) -> str:
        """Dev-friendly representation"""
        return f"TransactionData(id={self.id}, {self.type} {self.quantity} shares)"
    
    def __str__(self) -> str:
        """User-friendly representation"""
        return (f"{self.type} {self.quantity:.2f} shares"
            f"at {self.price:.2f}"
            f"(fee: {self.fee:.2f})")
        
    @property
    def is_buy(self) -> bool:
        """Check if this is a buy transaction"""
        return self.type == "BUY"
        
        
    @property
    def is_sell(self) -> bool:
        """Check if this is a sell transaction"""
        return self.type == "SELL"
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost (quantity x price + fee)"""
        return (self.quantity * self.price) + self.fee
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal without fee"""
        return self.quantity * self.price


######################################      TESTS      ######################################  
    
if __name__ == "__main__":
    print("=== Tests TransactionData ===\n")
    
    # Test 1: Achat (BUY)
    buy_transaction = TransactionData(
        id=1,
        portfolio_id=1,
        stock_id=1,
        type='BUY',
        quantity=10.0,
        price=150.0,
        fee=5.0,
        transaction_date=dt.datetime.now()
    )
    
    print("Test 1 - Achat:")
    print(f"  str():  {buy_transaction}")
    print(f"  repr(): {repr(buy_transaction)}")
    print(f"  is_buy: {buy_transaction.is_buy}")
    print(f"  total_cost: {buy_transaction.total_cost:.2f}€")
    
    # Test 2: Vente (SELL)
    sell_transaction = TransactionData(
        id=2,
        portfolio_id=1,
        stock_id=1,
        type='SELL',
        quantity=5.0,
        price=160.0,
        fee=3.0
    )
    
    print("\nTest 2 - Vente:")
    print(f"  str():  {sell_transaction}")
    print(f"  is_sell: {sell_transaction.is_sell}")
    print(f"  subtotal: {sell_transaction.subtotal:.2f}€")
    
    # Test 3: Immutabilité
    print("\nTest 3 - Immutabilité:")
    try:
        buy_transaction.price = 200.0
        print("  ❌ Modification réussie")
    except Exception as e:
        print(f"  ✅ Immutable: {type(e).__name__}")