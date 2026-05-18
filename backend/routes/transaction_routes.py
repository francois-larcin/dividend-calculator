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
    TransactionService
)
import yfinance as yf

transaction_bp = Blueprint('transaction', __name__)

transaction_service: TransactionService = None

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
    
    return jsonify({'message': 'Portfolio deleted'}), 200

