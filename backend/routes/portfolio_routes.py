"""
Portfolio Routes
================
REST API endpoints for portfolio management.

Endpoints:
    GET    /api/portfolios/             → Get all portfolios
    GET    /api/portfolios/<id>         → Get portfolio by ID
    GET    /api/portfolios/<id>/holdings → Get portfolio with holdings
    GET    /api/portfolios/<id>/gain   → Get portfolio total gain + value
    
    POST   /api/portfolios/             → Create portfolio
    PUT    /api/portfolios/<id>         → Update portfolio
    DELETE /api/portfolios/<id>         → Delete portfolio
"""

from flask import Blueprint, jsonify, request
from dataclasses import asdict

from backend.services import (
    PortfolioService
)

import yfinance as yf


#Blueprint
portfolio_bp = Blueprint('portfolio', __name__)

#Injected service (initialized in app.py)
portfolio_service: PortfolioService = None

# ==========================================
# READ
# ==========================================

@portfolio_bp.route('/', methods=['GET'])
def get_all_user_portfolios():
    """
    GET /api/portfolios/
    
    Returns all portfolios.
    
    Response 200:
        [{"id": 1, "name": "Mon Portfolio", "currency": "EUR"}, ...]
    """
    # TODO: ID get from JWT token
    portfolios = portfolio_service.get_user_portfolios(user_id=1)
    
    return jsonify([asdict(p) for p in portfolios]), 200


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id: int):
    """
    GET /api/portfolios/<portfolio_id>
    
    Returns portfolio by ID.
    
    Response 200: {"id": 1, "name": "Mon Portfolio", ...}
    Response 404: {"error": "Portfolio not found"}
    """
    
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    
    if portfolio is None: 
        return jsonify({"error": f"Portfolio {portfolio_id} not found"}), 404
    
    return jsonify(asdict(portfolio)), 200


@portfolio_bp.route('/<int:portfolio_id>/holdings', methods=['GET'])
def get_portfolio_with_holdings(portfolio_id: int):
    """
    GET /api/portfolios/<portfolio_id>/holdings
    
    Returns portfolio with all holdings loaded.
    
    Response 200: {"id": 1, "name": "...", "holdings": [...]}
    Response 404: {"error": "Portfolio not found"}
    """
    portfolio = portfolio_service.get_portfolio_with_holdings(portfolio_id)
    
    if portfolio is None:
        return jsonify({'error': f"Portfolio {portfolio_id} not found"}), 404
    
    return jsonify(asdict(portfolio)), 200


# ==========================================
# CALCULATE
# ==========================================


@portfolio_bp.route('/<int:portfolio_id>/gain', methods=['GET'])   
def get_portfolio_gain(portfolio_id: int):
    """
    GET /api/portfolios/<portfolio_id>/gain

    Returns a dict with total invested, current value, gain and gain_percent

    Response 200: {"total_invested": 1000, "current_value": 1200, "gain":200, "gain_percent":20}
    Response 404: {"error": "Portfolio not found"}
    """ 
    
    portfolio = portfolio_service.get_portfolio_with_holdings(portfolio_id)
    
    if portfolio is None:
       return jsonify({'error': f"Portfolio {portfolio_id} not found"}), 404 
   
    current_prices = {}
    for holding in portfolio.holdings:
        ticker = yf.Ticker(holding.ticker)
        info = ticker.info
        
        current_prices[holding.stock_id] = info.get('currentPrice', 0.0)
        
        
    data = portfolio_service.calculate_portfolio_gain(portfolio_id, current_prices)
    
    return jsonify(data), 200
    
# ==========================================
# CREATE
# ==========================================

@portfolio_bp.route('/', methods=['POST'])
def create_portfolio():
    """
    POST /api/portfolios
    
    Body JSON:
        {"user_id": 1, "name": "Mon Portfolio", "currency": "EUR"}
    
    Response 201: {"id": 5}
    Response 400: {"error": "Missing required field: name"}
    """
    
    data = request.get_json()
    
    #Validate required fields
    required_fields = ['user_id', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"Missing required field: {field}"}), 400
        
    portfolio_id = portfolio_service.create_portfolio(
        user_id=data['user_id'],
        name=data['name'],
        currency=data.get('currency', 'EUR') #EUR by default
    )
    
    return jsonify({'id': portfolio_id}), 201
    
# ==========================================
# UPDATE -> PATCH
# ==========================================

@portfolio_bp.route('/<int:portfolio_id>', methods=['PATCH'])
def update_portfolio(portfolio_id: int):
    """
    PUT /api/portfolios/<portfolio_id>
    
    Body JSON:
        {"name": "Nouveau Nom", "currency": "USD"}
    
    Response 200: {"message": "Portfolio updated"}
    Response 404: {"error": "Portfolio not found"}
    """
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    
    data = request.get_json()
    
    #Update only provided fields
    portfolio.name = data.get('name', portfolio.name)
    portfolio.currency = data.get('currency', portfolio.currency)
    
    portfolio_service.update_portfolio(portfolio)
    
    return jsonify({'message': 'Portfolio updated'}), 200

# ==========================================
# DELETE
# ==========================================

@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
def delete_portfolio(portfolio_id: int):
    """
    DELETE /api/portfolios/<portfolio_id>
    
    Response 200: {"message": "Portfolio deleted"}
    Response 404: {"error": "Portfolio not found"}
    """
    
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    
    portfolio_service.delete_portfolio(portfolio_id)
    
    return jsonify({'message': 'Portfolio deleted'}), 200
