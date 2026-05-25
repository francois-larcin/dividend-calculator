"""
Dividend payment Routes
================
REST API endpoints for Dividend payment management.

Endpoints:

    GET    /api/dividends/<portfolio_id>             → Get all div_payment for a portfolio
    GET    /api/dividends/<portfolio_id>/total       → Get total received for a portfolio
    GET    /api/dividends/<portfolio_id>/yield       → Get portfolio yield
    
    
    GET    /api/dividends/<portfolio_id>/<stock_id>  → Get all div_payment for a stock in a portfolio  
    
    
    POST   /api/dividends/sync/<portfolio_id>        → Create buy transaction
    DELETE /api/dividends/<id>                       → Delete div_payment
"""

from flask import Blueprint, jsonify, request
from dataclasses import asdict

from backend.services import (
    DividendPaymentService
)

div_payment_bp = Blueprint('dividend_payment', __name__)

div_payment_service: DividendPaymentService = None

# ==========================================
# READ
# ==========================================

@div_payment_bp.route('/portfolio/<int:portfolio_id>', methods=['GET'])
def get_portfolio_div_payment(portfolio_id: int):
    """
    GET /api/dividends/portfolio/<portfolio_id>
    
    Returns dividend payments by portfolio
    
    Response 200: [
        {"portfolio_id": 1, "stock_id": 2, "amount_per_share": 3.45},
        {"portfolio_id": 1, "stock_id": 3, "amount_per_share": 18.89}, ...
    ]
    """
    
    dividend_payments = div_payment_service.get_portfolio_div_payment(portfolio_id)
    
    return jsonify([asdict(d) for d in dividend_payments]), 200

@div_payment_bp.route('/portfolio/<int:portfolio_id>/total', methods=['GET'])
def get_portfolio_total_div_received(portfolio_id: int):
    """
    GET /api/dividends/<portfolio_id>/total
    
    Returns total of all dividend received for a portfolio
    
    Response 200: {"total_dividend": 345.98}
    """
    
    total = div_payment_service.get_total_dividend_received_by_portfolio(portfolio_id)
    
    return jsonify({"total_dividends": total}), 200


@div_payment_bp.route('/portfolio/<int:portfolio_id>/yield', methods=['GET'])
def get_portfolio_dividend_yield(portfolio_id: int):
    """
    GET /api/dividends/<portfolio_id>/yield
    
    Returns portfolio dividend yield to total invested
    
    Response 200: {"portfolio_dividend_yield": 5.43}
    """
    
    dividend_yield = div_payment_service.calculate_portfolio_dividend_yield(portfolio_id)
    
    return jsonify({"dividend_yield": dividend_yield}), 200
    
    

@div_payment_bp.route('/portfolio/<int:portfolio_id>/stock/<int:stock_id>', methods=['GET'])
def get_portfolio_dividend_stock(portfolio_id: int, stock_id: int):
    """
    GET /api/dividends/<portfolio_id>/stock/<stock_id>
    
    Returns div payment by stock in a portfolio
    
    Response 200: [
        {"portfolio_id": 1, "stock_id": 3, "amount_per_share": 3.45},
        {"portfolio_id": 1, "stock_id": 3, "amount_per_share": 18.89}, ...
    ]
    """
    
    dividend_payments = div_payment_service.get_by_portfolio_stock_div_payment(portfolio_id, stock_id)
    
    return jsonify([asdict(d) for d in dividend_payments]), 200


# ==========================================
# CREATE
# ==========================================

@div_payment_bp.route('/sync/<int:portfolio_id>', methods=['POST'])
def sync_dividends(portfolio_id: int):
    """
    Sync dividend payments from yfinance for all portfolio holdings
    
    Returns:
        Number of new dividend payments inserted
        
    Reponse 200: {"New dividend payments": 3}
    """
    
    nb_new_div_payments = div_payment_service.sync_dividends(portfolio_id)
    
    return jsonify({'number or new div payments inserted': nb_new_div_payments}), 200
    



    
# ==========================================
# UPDATE
# ==========================================


