"""
Holding Routes
================
REST API endpoints for holding management.

Endpoints:
GET /api/holdings/<portfolio_id>                              → Get all holdings
GET /api/holdings/<portfolio_id>/<stock_id>                   → Get specific holding
GET /api/holdings/<portfolio_id>/allocation/currency          → Allocation per currency
GET /api/holdings/<portfolio_id>/allocation/sector            → Allocation per sector
GET /api/holdings/<portfolio_id>/dividend-ratio               → Dividend ratio
GET /api/holdings/<portfolio_id>/<stock_id>/dividend-history  → Dividend history
"""

from flask import Blueprint, jsonify, request
from dataclasses import asdict

from backend.services import (
    HoldingService,
    PortfolioService
)

holding_bp = Blueprint('holding', __name__)
holding_service: HoldingService = None
portfolio_service: PortfolioService = None

# ==========================================
# READ
# ==========================================

@holding_bp.route('/<int:portfolio_id>', methods=['GET'])
def get_portfolio_holdings(portfolio_id: int):
    """
    GET /api/holdings/<portfolio_id>

    Returns holdings from a portfolio.

    Response 200: [
        {"stock_id": 2, "ticker": "VIST", "company_name" "Vista Energy", ...},
        {"stock_id": 3, "ticker": "MSFT", "company_name" "Microsfot Corp", ...},
    ]
    Response 404: {"error": "stock not found"}
    """ 
    
    holdings = holding_service.get_portfolio_holdings(portfolio_id)
    
    return jsonify([asdict(h) for h in holdings]), 200


@holding_bp.route('/<int:portfolio_id>/<int:stock_id>', methods=['GET'])
def get_holding(portfolio_id: int, stock_id: int):
    """
    GET /api/holdings/<portfolio_id>/<stock_id>

    Returns holding by portfolio ID and stock ID.

    Response 200: {"stock_id": 2, "ticker": "VIST", "company_name" "Vista Energy", ...}
    Response 404: {"error": "Transaction not found"}
    """ 
    holding = holding_service.get_holding(portfolio_id, stock_id)
    
    if holding is None:
        return jsonify({'error': f"Portfolio {portfolio_id} or stock {stock_id} not found"})
    
    return jsonify(asdict(holding)), 200
 
    
@holding_bp.route('/<int:portfolio_id>/allocation/sector', methods=['GET'])
def get_allocation_by_sector(portfolio_id: int):
    """
    GET /api/holdings/<portfolio_id>/allocation/sector
    
    Response 200: {"Energy": 13.60, "Industrial": 12.00, "Technology": 30.32, ...}
    
    """
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    
    sector_allocation = holding_service.get_portfolio_allocation_by_sector(portfolio_id)
    
    return jsonify(sector_allocation), 200


@holding_bp.route('/<int:portfolio_id>/allocation/currency', methods=['GET'])
def get_allocation_by_currency(portfolio_id: int):
    """
    GET /api/holdings/<portfolio_id>/allocation/currency
    
    Response 200: {"Energy": 13.60, "Industrial": 12.00, "Technology": 30.32, ...}
    
    """
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    
    currency_allocation = holding_service.get_portfolio_allocation_by_currency(portfolio_id)
    
    return jsonify(currency_allocation), 200 


@holding_bp.route('/<int:portfolio_id>/<int:stock_id>/dividend-history', methods=['GET'])
def get_holding_dividend_history(portfolio_id: int, stock_id: int):
    """
    GET /api/holdings/<portfolio_id>/<stock_id>/dividend-history
    
    Response 200: {
        'holding': {"stock_id": 2, "ticker": "VIST", "company_name" "Vista Energy", ...},
        'dividends': [
            {portfolio_id: 2, stock_id: 2, amount_per_share: 3, total_amount: 9, ...}, 
            {portfolio_id: 2, stock_id: 2, amount_per_share: 3.3, total_amount: 9.9, ...}
        ]}
    """
    
    holding = holding_service.get_holding(portfolio_id, stock_id)
    
    if holding is None:
        return jsonify({'error': f"Portfolio {portfolio_id} or stock {stock_id} not found"})
    
    dividend_history = holding_service.get_holding_dividend_history(portfolio_id, stock_id)
    
    return jsonify({
        'holding': asdict(dividend_history['holding']),
        'dividends': [asdict(d) for d in dividend_history['dividends']]
    }), 200


@holding_bp.route('/<int:portfolio_id>/dividend-ratio', methods=['GET'])
def get_holding_dividend_ratio_to_portfolio(portfolio_id: int):
    """
    GET /api/holdings/<portfolio_id>/dividend-ratio
    """
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 400
    
    dividend_ratio = holding_service.get_holding_dividend_ratio_to_portfolio(portfolio_id)
    
    return jsonify(dividend_ratio), 200
    