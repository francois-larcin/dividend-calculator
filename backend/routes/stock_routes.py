"""
Stock Routes
================
REST API endpoints for stock management.

Endpoints:
    GET  /api/stocks/<id>                     → GET stock by ID
    GET  /api/stocks/search?q=                → Live search
    GET  /api/stocks/sector/<ticker>          → GET stock by ticker
    
    POST  /api/stocks/<id>/refresh            → Refresh 1 stock from yfinance
    POST  /api/stocks/refresh-all             → Refresh all from yfinance
    DELETE /api/stock/<id>                    → Delete stock
"""

from flask import Blueprint, jsonify, request
from dataclasses import asdict

from backend.services import (
    StockService
)

import yfinance as yf

stock_bp = Blueprint('stock', __name__)

stock_service: StockService = None

# ==========================================
# READ
# ==========================================



@stock_bp.route('/search', methods=['GET'])
def search_stocks():
    """
    GET /api/stocks/search?q=

    Returns a list of dict of company_name + ticker corresponding to the search

    Response 200: [
        {"name": "VISA", "ticker": "V"},
        {"name": "Vista Energy", "ticker": "VIST"}
    ]
    """
    query = request.args.get('q', '')
    
    results = stock_service.search_stocks(query)
    return (jsonify(results))

@stock_bp.route('/<int:stock_id>', methods=['GET'])
def get_stock(stock_id: int):
    """
    GET /api/stocks/<stock_id>

    Returns stock by ID.

    Response 200: {"name": "Vista Energy", "ticker": "VIST"}
    Response 404: {"error": "stock not found"}
    """ 
    
    stock = stock_service.get_stock(stock_id)
    
    if stock is None:
        return jsonify({'error': f"Stock {stock_id} not found"}), 404
    
    return jsonify(asdict(stock)), 200


@stock_bp.route('/<ticker>', methods=['GET'])
def get_stock_by_ticker(ticker: str):
    """
    GET /api/stocks/<ticker>

    Returns stock by ticker.

    Response 200: {"name": "Vista Energy", "ticker": "VIST"}
    Response 404: {"error": "stock not found"}
    """ 
    
    stock = stock_service.get_stocks_by_ticker(ticker)
    
    if stock is None:
        return jsonify({'error': f"Stock {ticker} not found"}), 404
    
    return jsonify(asdict(stock)), 200


# ==========================================
# UPDATE
# ==========================================

@stock_bp.route('/<int:stock_id>/refresh', methods=['POST'])
def refresh_stock(stock_id: int):
    """
    POST /api/stocks/<stock_id>/refresh
    
    Response 200: {"name": "Vista Energy", "ticker": "VIST"}
    Response 404: {"error": "Stock not found"}
    """
    
    stock = stock_service.refresh_one_stock(stock_id)
    
    if stock is None:
        return jsonify({'error': f'Stock {stock_id} not found'}), 404
    
    return jsonify(asdict(stock)), 200


@stock_bp.route('/refresh-all', methods=['POST'])
def refresh_stocks():
    """
    POST /api/stocks/refresh-all
    
    Response 200: {"stocks refreshed": 123}
    """
    
    nb_refreshed_stocks = stock_service.refresh_all_stocks()
    
    return jsonify({'number of refreshed stocks': nb_refreshed_stocks}), 200

@stock_bp.route('/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id: int):
    """
    DELETE /api/stocks/<stock_id>
    
    Response 200: {"message": "stock deleted"}
    Response 404: {"error": "stock not found"}
    """
    
    stock = stock_service.get_stock(stock_id)
    
    if stock is None:
        return jsonify({"error": f"Stock {stock_id} not found"}), 404
    
    stock_service.delete_stock(stock_id)
    
    return jsonify({'message': 'Stock deleted'}), 200
    