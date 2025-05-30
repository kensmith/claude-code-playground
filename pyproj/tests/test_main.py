import pytest
import pandas as pd
from unittest.mock import Mock, patch
from pyproj.main import TickerService, get_gold_and_dxy


class TestTickerService:
    def test_get_ticker_price_success(self, mocker):
        # Mock yfinance.Ticker
        mock_ticker = Mock()
        mock_history = pd.DataFrame({'Close': [100.50, 101.25, 102.00]})
        mock_ticker.history.return_value = mock_history
        
        mocker.patch('pyproj.main.yf.Ticker', return_value=mock_ticker)
        
        service = TickerService()
        price = service.get_ticker_price("TEST")
        
        assert price == 102.00
        mock_ticker.history.assert_called_once_with(period="1d")
    
    def test_get_ticker_price_empty_history(self, mocker):
        # Mock yfinance.Ticker with empty DataFrame
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()
        
        mocker.patch('pyproj.main.yf.Ticker', return_value=mock_ticker)
        
        service = TickerService()
        price = service.get_ticker_price("TEST")
        
        assert price is None
    
    def test_get_ticker_price_exception(self, mocker):
        # Mock yfinance.Ticker to raise exception
        mocker.patch('pyproj.main.yf.Ticker', side_effect=Exception("Network error"))
        
        service = TickerService()
        price = service.get_ticker_price("TEST")
        
        assert price is None
    
    def test_get_multiple_tickers(self, mocker):
        service = TickerService()
        
        # Mock the get_ticker_price method
        mocker.patch.object(service, 'get_ticker_price', side_effect=[100.50, 95.25])
        
        symbols = {"Stock A": "STOCK_A", "Stock B": "STOCK_B"}
        result = service.get_multiple_tickers(symbols)
        
        expected = {"Stock A": 100.50, "Stock B": 95.25}
        assert result == expected


class TestGetGoldAndDxy:
    def test_get_gold_and_dxy(self, mocker, capsys):
        # Mock TickerService
        mock_service = Mock()
        mock_service.get_multiple_tickers.return_value = {
            "Gold Price": 3313.40,
            "DXY Dollar Index": 99.44
        }
        
        mocker.patch('pyproj.main.TickerService', return_value=mock_service)
        
        result = get_gold_and_dxy()
        
        expected = {"Gold Price": 3313.40, "DXY Dollar Index": 99.44}
        assert result == expected
        
        # Check console output
        captured = capsys.readouterr()
        assert "Gold Price (GC=F): $3313.40" in captured.out
        assert "DXY Dollar Index: 99.44" in captured.out
    
    def test_get_gold_and_dxy_unavailable_data(self, mocker, capsys):
        # Mock TickerService with None values
        mock_service = Mock()
        mock_service.get_multiple_tickers.return_value = {
            "Gold Price": None,
            "DXY Dollar Index": None
        }
        
        mocker.patch('pyproj.main.TickerService', return_value=mock_service)
        
        result = get_gold_and_dxy()
        
        expected = {"Gold Price": None, "DXY Dollar Index": None}
        assert result == expected
        
        # Check console output
        captured = capsys.readouterr()
        assert "Gold Price: unavailable" in captured.out
        assert "DXY Dollar Index: unavailable" in captured.out
