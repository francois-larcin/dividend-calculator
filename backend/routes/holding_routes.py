"""
Holding Routes
================
REST API endpoints for holding management.

Endpoints:
GET /api/holdings/<portfolio_id>                              → Get all holdings
GET /api/holdings/<portfolio_id>/detail                    → Get all holdings with gain data

GET /api/holdings/<portfolio_id>/<stock_id>                   → Get specific holding
GET /api/holdings/<portfolio_id>/allocation/currency          → Allocation per currency
GET /api/holdings/<portfolio_id>/allocation/sector            → Allocation per sector
GET /api/holdings/<portfolio_id>/dividend-ratio               → Dividend ratio
GET /api/holdings/<portfolio_id>/<stock_id>/dividend-history  → Dividend history


"""

from flask import Blueprint, jsonify, request
from dataclasses import asdict

from backend.models.holding import HoldingData
from backend.services import (
    HoldingService,
    PortfolioService,
    DividendPaymentService
)

holding_bp = Blueprint('holding', __name__)
holding_service: HoldingService = None
portfolio_service: PortfolioService = None
div_payment_service: DividendPaymentService = None

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


@holding_bp.route('/<int:portfolio_id>/detail', methods=['GET'])
def get_holdings_with_detail(portfolio_id: int):
    """
    GET /api/holdings/<portfolio_id>/detail
    
    Returns 200 : [
        {"stock_id": 2, ..., "stock_price": 75, "current_value": 2500, "gain": 348...},
        {"stock_id": 2, ..., "stock_price": 19, "current_value": 1800, "gain": 134...},
    ]
    Response 404: {"error": "stock not found"}
    """
    
    holdings = holding_service.get_all_holdings_detail(portfolio_id)
    
    return jsonify(holdings), 200
    

@holding_bp.route('/<int:portfolio_id>/<int:stock_id>', methods=['GET'])
def get_holding(portfolio_id: int, stock_id: int):
    """
    GET /api/holdings/<portfolio_id>/<stock_id>

    Returns holding by portfolio ID and stock ID.

    Response 200: {"stock_id": 2, "ticker": "VIST", "company_name": "Vista Energy", ...}
    Response 404: {"error": "Holding or Portfolio not found"}
    """ 
    holding = holding_service.get_holding(portfolio_id, stock_id)
    
    if holding is None:
        return jsonify({'error': f"Portfolio {portfolio_id} or stock {stock_id} not found"})
    
    return jsonify(asdict(holding)), 200

@holding_bp.route('/<int:portfolio_id>/<int:stock_id>/detail', methods=['GET'])
def get_holding_with_detail(portfolio_id: int, stock_id: int):
    """
    GET /api/holdings/<portfolio_id>/<stock_id>

    Returns holding with detail by portfolio ID and stock ID.

    Response 200: {"stock_id": 2, "ticker": "VIST", "weight": 6.6, ...}
    Response 404: {"error": "Holding or Portfolio not found"}
    """
    
    detail = holding_service.get_one_holding_detail(portfolio_id, stock_id)
    
    if detail is None:
        return jsonify({'error': 'Holding not found'}), 404
    
    return jsonify(detail), 200
    

 
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
def get_holdings_dividend_ratio_to_portfolio(portfolio_id: int):
    """
    GET /api/holdings/<portfolio_id>/dividend-ratio
    """
    portfolio = portfolio_service.get_portfolio(portfolio_id)
    
    if portfolio is None:
        return jsonify({'error': f'Portfolio {portfolio_id} not found'}), 404
    
    portfolio_total_dividends = div_payment_service.get_total_dividend_received_by_portfolio(portfolio_id)
    
    dividend_ratio = holding_service.get_holdings_dividend_ratio_to_portfolio(portfolio_id, portfolio_total_dividends)
    
    return jsonify(dividend_ratio), 200
    