
"""
Flask Application
=================
Main entry point. Creates app, initializes services, registers routes.
"""

from flask import Flask

from backend.repositories import (
    PortfolioRepository,
    HoldingRepository,
    TransactionRepository,
    StockRepository,
    DividendPaymentRepository
)

from backend.services import (
    TransactionService, 
    PortfolioService,
    HoldingService,
    StockService,
    DividendPaymentService
)


from backend.routes import (
    portfolio_bp,
    transaction_bp,
    stock_bp,
    holding_bp,
    portfolio_routes,
    transaction_routes,
    stock_routes,
    holding_routes
)

# ==========================================
# CONFIGURATION
# ==========================================

db_config = {
    'host': 'localhost',
    'database': 'dividend_db',
    'user': 'dividend_user',
    'password': 'dividend123'
}

# ==========================================
# APP INITIALIZATION
# ==========================================

def create_app() -> Flask:
    """
    Create and configure Flask application.
    
    Returns:
        Configured Flask app
    """
    
    app = Flask(__name__)
    
    #Create repositories
    portfolio_repo = PortfolioRepository(db_config)
    holding_repo = HoldingRepository(db_config)
    transaction_repo = TransactionRepository(db_config)
    stock_repo = StockRepository(db_config)
    div_payment_repo = DividendPaymentRepository(db_config)
    
    #Create services (Dependency Injection)
    portfolio_service = PortfolioService(
        portfolio_repo=portfolio_repo,
        holding_repo=holding_repo,
        transaction_repo=transaction_repo
    )
    
    transaction_service = TransactionService(
        portfolio_repo = portfolio_repo,
        transaction_repo=transaction_repo,
        stock_repo=stock_repo,
        holding_repo=holding_repo,
    )
    
    stock_service = StockService(
        stock_repo=stock_repo
    )
    
    holding_service = HoldingService(
        holding_repo=holding_repo,
        stock_repo=stock_repo,
        div_payment_repo=div_payment_repo
    )
    
    #Inject service into routes
    portfolio_routes.portfolio_service = portfolio_service
    transaction_routes.transaction_service = transaction_service
    stock_routes.stock_service = stock_service
    holding_routes.holding_service = holding_service
    holding_routes.portfolio_service = portfolio_service
    
    
    #Register blueprints (URL prefixes)
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolios')
    app.register_blueprint(transaction_bp, url_prefix='/api/transactions')
    app.register_blueprint(stock_bp, url_prefix='/api/stocks')
    app.register_blueprint(holding_bp, url_prefix='/api/holdings')
    
    return app

# ==========================================
# RUN
# ==========================================

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
    