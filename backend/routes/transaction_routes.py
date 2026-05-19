"""
Transaction Routes
================
REST API endpoints for transaction management.

Endpoints:
    GET    /api/transactions/<id>                                       → Get transaction by ID
    GET    /api/transactions/portfolio/<portfolio_id>                   → Get transactions by portfolio
    GET    /api/transactions/stock/<stock_id>                           → Get transactions by stock
    GET    /api/transactions/portfolio/<portfolio_id>/stock/<stock_id>  → Get transactions by stock in a portfolio
    
    POST   /api/transactions/buy                                        → Create buy transaction
    POST   /api/transactions/sell                                       → Create sell transaction
    DELETE /api/transactions/<id>                                       → Delete transaction
"""

from flask import Blueprint, jsonify, request
from dataclasses import asdict

from backend.services import (
    TransactionService,
    PortfolioService,
    StockService
)
import yfinance as yf

transaction_bp = Blueprint('transaction', __name__)

transaction_service: TransactionService = None
portfolio_service: PortfolioService = None
stock_service: StockService = None

# ==========================================
# READ
# ==========================================

@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id: int):
    """
    GET /api/transactions/<transaction_id>

    Returns transaction by ID.

    Response 200: {"portfolio_id": 1, "stock_id": 3, "type": "BUY"...}
    Response 404: {"error": "Transaction not found"}
    """ 
    
    transaction = transaction_service.get_transaction(transaction_id)
    
    if transaction is None:
        return jsonify({"error": f"Transaction {transaction_id} not found"}), 404 
    
    return jsonify(asdict(transaction)), 200


@transaction_bp.route('/portfolio/<portfolio_id>', methods=['GET'])
def get_portfolio_transactions(portfolio_id: int):
    """
    GET /api/transactions/portfolio/<portfolio_id> 

    Returns transactions by portfolio

    Response 200: [
        {"portfolio_id": 1, "stock_id": 3, "type": "BUY"...},
        {"portfolio_id": 1, "stock_id": 2, "type": "SELL"...}, ...
        ]
    """
    
    transactions = transaction_service.get_portfolio_transactions(portfolio_id)
    
    return jsonify([asdict(t) for t in transactions]), 200
   

@transaction_bp.route('/stock/<int:stock_id>', methods=['GET'])
def get_stock_transactions(stock_id: int):
    """
    GET /api/transactions/stock/<stock_id> 

    Returns transactions by stock

    Response 200: [
        {"portfolio_id": 1, "stock_id": 3, "type": "BUY"...},
        {"portfolio_id": 1, "stock_id": 2, "type": "SELL"...}, ...
        ]
    """
    
    transactions = transaction_service.get_stock_transactions(stock_id)
    
    return jsonify([asdict(t) for t in transactions]), 200

 
@transaction_bp.route('portfolio/<int:portfolio_id>/stock/<int:stock_id>', methods=['GET'])
def get_portfolio_stock_transaction(portfolio_id: int, stock_id: int):
    """
    GET /api/transactions/portfolio/<portfolio_id>/stock/<stock_id>

    Returns transaction by stock in a portfolio

    Response 200: [
        {"portfolio_id": 1, "stock_id": 3, "type": "BUY"...},
        {"portfolio_id": 1, "stock_id": 2, "type": "SELL"...}, ...
        ]
    """
    
    transactions = transaction_service.get_portfolio_stock_transactions(portfolio_id, stock_id)
    
    return jsonify([asdict(t) for t in transactions]), 200

  
# ==========================================
# CREATE
# ==========================================

@transaction_bp.route('/buy', methods=['POST'])
def create_buy_transaction():
    """
    POST /api/transactions/buy
    
    Body JSON:
        {"portfolio_id": 1, "ticker": "MSFT", "quantity": 50, "price": 14.5, "fee": 2}
        
    Response 201: {"id": 5}
    Response 400: {"error": "Missing required field: quantity"}
    """
    
    data = request.get_json()
    
    #Validate required fields
    required_fields = ["portfolio_id", "ticker", "quantity", "price"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
        
    transaction_id = transaction_service.buy_stock(
        portfolio_id=data["portfolio_id"],
        ticker=data["ticker"],
        quantity=data["quantity"],
        price=data["price"],
        fee=data.get("fee", 0.0)
    )
    
    return jsonify({"id": transaction_id}), 201

@transaction_bp.route('/sell', methods=['POST'])
def create_sell_transaction():
    """
    POST /api/transactions/sell
    
    Body JSON:
        {"portfolio_id": 1, "ticker": "NVDA", "quantity": 30, "price": 199, "fee": 1.67}
        
    Response 201: {"id": 5}
    Response 400: {"error": "Missing required field: quantity"}
    """
    
    data = request.get_json()
    
    #Validate required fields
    required_fields = ["portfolio_id", "ticker", "quantity", "price"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
        
    transaction_id = transaction_service.sell_stock(
        portfolio_id=data["portfolio_id"],
        ticker=data["ticker"],
        quantity=data["quantity"],
        price=data["price"],
        fee=data.get("fee", 0.0)
    )
    
    return jsonify({"id": transaction_id}), 201
# ==========================================
# DELETE
# ==========================================

@transaction_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id: int):
    """
    DELETE /api/transactions/<transaction_id>
    
    Response 200: {"message": "Transaction deleted"}
    Response 404: {"error": "Transaction not found"}
    """
    
    transaction = transaction_service.get_transaction(transaction_id)
    
    if transaction is None:
        return jsonify({"error": f"Transaction {transaction_id} not found"}), 404 
    
    transaction_service.delete_transaction(transaction_id)
    
    return jsonify({'message': 'Transaction deleted'}), 200



