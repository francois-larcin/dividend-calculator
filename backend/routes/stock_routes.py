"""
Stock Routes
================
REST API endpoints for stock management.

Endpoints:
    GET  /api/stocks/                            → GET all stocks 
    GET  /api/stocks/<id>                        → GET stock by ID
    GET  /api/stocks/search?q=                   → Live search
    GET  /api/stocks/sector/<sector>             → GET stock by ticker
    
    POST  /api/stocks/<id>/refresh               → Refresh from yfinance
    DELETE /api/stock/<id>                       → Delete stock
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
    GET /api/stocks/search

    Returns a list of dict of company_name + ticker corresponding to the search

    Response 200: [
        {"name": "VISA", "ticker": "V"},
        {"name": "Vista Energy", "ticker": "VIST"}
    ]
    """
    query = request.args.get('q', '')
    
    results = stock_service.search_stocks(query)
    return (jsonify(results))