import pandas as pd
from unittest.mock import Mock, patch
from pyproj.main import TickerService, get_gold_and_dxy, get_all_market_data


class TestTickerService:
    def test_get_ticker_price_success(self, mocker):
        # Mock yfinance.Ticker
        mock_ticker = Mock()
        mock_history = pd.DataFrame({"Close": [100.50, 101.25, 102.00]})
        mock_ticker.history.return_value = mock_history

        mocker.patch("pyproj.main.yf.Ticker", return_value=mock_ticker)

        service = TickerService()
        price = service.get_ticker_price("TEST")

        assert price == 102.00
        mock_ticker.history.assert_called_once_with(period="1d")

    def test_get_ticker_price_empty_history(self, mocker):
        # Mock yfinance.Ticker with empty DataFrame
        mock_ticker = Mock()
        mock_ticker.history.return_value = pd.DataFrame()

        mocker.patch("pyproj.main.yf.Ticker", return_value=mock_ticker)

        service = TickerService()
        price = service.get_ticker_price("TEST")

        assert price is None

    def test_get_ticker_price_exception(self, mocker):
        # Mock yfinance.Ticker to raise exception
        mocker.patch("pyproj.main.yf.Ticker", side_effect=Exception("Network error"))

        service = TickerService()
        price = service.get_ticker_price("TEST")

        assert price is None

    def test_get_multiple_tickers(self, mocker):
        service = TickerService()

        # Mock the get_ticker_price method
        mocker.patch.object(service, "get_ticker_price", side_effect=[100.50, 95.25])

        symbols = {"Stock A": "STOCK_A", "Stock B": "STOCK_B"}
        result = service.get_multiple_tickers(symbols)

        expected = {"Stock A": 100.50, "Stock B": 95.25}
        assert result == expected


class TestGetGoldAndDxy:
    @patch("pyproj.main.requests.post")
    @patch("pyproj.main.os.getenv")
    def test_get_gold_and_dxy(self, mock_getenv, mock_post, mocker, capsys):
        # Mock TickerService
        mock_service = Mock()
        mock_service.get_multiple_tickers.return_value = {
            "Gold Price": 3313.40,
            "DXY Dollar Index": 99.44,
        }

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mock environment variable
        mock_getenv.return_value = "https://ntfy.sh/test-endpoint"
        
        mocker.patch("pyproj.main.TickerService", return_value=mock_service)

        result = get_gold_and_dxy()

        expected = {
            "Gold Price": 3313.40,
            "DXY Dollar Index": 99.44,
        }
        assert result == expected

        # Check that ntfy.sh was called
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://ntfy.sh/test-endpoint"
        assert kwargs["data"] == "Gold Price: $3313.40\nDXY Dollar Index: 99.4400"
        assert kwargs["headers"]["Title"] == "Legacy Market Data"

        # Check console output
        captured = capsys.readouterr()
        assert "Legacy market data sent to ntfy.sh successfully" in captured.out

    @patch("pyproj.main.requests.post")
    @patch("pyproj.main.os.getenv")
    def test_get_gold_and_dxy_unavailable_data(self, mock_getenv, mock_post, mocker, capsys):
        # Mock TickerService with None values
        mock_service = Mock()
        mock_service.get_multiple_tickers.return_value = {
            "Gold Price": None,
            "DXY Dollar Index": None,
        }

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mock environment variable
        mock_getenv.return_value = "https://ntfy.sh/test-endpoint"

        mocker.patch("pyproj.main.TickerService", return_value=mock_service)

        result = get_gold_and_dxy()

        expected = {
            "Gold Price": None,
            "DXY Dollar Index": None,
        }
        assert result == expected

        # Check that ntfy.sh was called with unavailable data
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://ntfy.sh/test-endpoint"
        assert kwargs["data"] == "Gold Price: unavailable\nDXY Dollar Index: unavailable"
        assert kwargs["headers"]["Title"] == "Legacy Market Data"

        # Check console output
        captured = capsys.readouterr()
        assert "Legacy market data sent to ntfy.sh successfully" in captured.out

    @patch("pyproj.main.os.getenv")
    def test_get_gold_and_dxy_no_endpoint(self, mock_getenv, mocker, capsys):
        # Mock TickerService
        mock_service = Mock()
        mock_service.get_multiple_tickers.return_value = {
            "Gold Price": 3313.40,
            "DXY Dollar Index": 99.44,
        }

        # Mock environment variable as None
        mock_getenv.return_value = None
        
        mocker.patch("pyproj.main.TickerService", return_value=mock_service)

        result = get_gold_and_dxy()

        expected = {
            "Gold Price": 3313.40,
            "DXY Dollar Index": 99.44,
        }
        assert result == expected

        # Check console output
        captured = capsys.readouterr()
        assert "Warning: NTFY_SH_ENDPOINT environment variable not set" in captured.out


class TestGetAllMarketData:
    @patch("pyproj.main.requests.post")
    @patch("pyproj.main.os.getenv")
    def test_get_all_market_data(self, mock_getenv, mock_post, mocker, capsys):
        # Mock TickerService
        mock_service = Mock()
        mock_service.get_multiple_tickers.return_value = {
            "Gold Price": 3313.40,
            "Oil Price (WTI)": 75.50,
            "DXY Dollar Index": 99.44,
            "USD/EUR": 1.0850,
            "USD/JPY": 150.25,
            "USD/CNH": 7.25,
            "USD/TWD": 31.50,
            "BTC/USD": 65000.00,
            "VIX": 20.15,
            "MOVE Index": 95.30,
            "NASDAQ": 15500.75,
        }

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Mock environment variable
        mock_getenv.return_value = "https://ntfy.sh/test-endpoint"
        
        mocker.patch("pyproj.main.TickerService", return_value=mock_service)

        result = get_all_market_data()

        expected = {
            "Gold Price": 3313.40,
            "Oil Price (WTI)": 75.50,
            "DXY Dollar Index": 99.44,
            "USD/EUR": 1.0850,
            "USD/JPY": 150.25,
            "USD/CNH": 7.25,
            "USD/TWD": 31.50,
            "BTC/USD": 65000.00,
            "VIX": 20.15,
            "MOVE Index": 95.30,
            "NASDAQ": 15500.75,
        }
        assert result == expected

        # Check that ntfy.sh was called
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://ntfy.sh/test-endpoint"
        assert kwargs["headers"]["Title"] == "Market Data Update"
        assert "Gold Price: $3313.40" in kwargs["data"]
        assert "BTC/USD: $65,000.00" in kwargs["data"]

        # Check console output
        captured = capsys.readouterr()
        assert "Market data sent to ntfy.sh successfully" in captured.out

    @patch("pyproj.main.os.getenv")
    def test_get_all_market_data_no_endpoint(self, mock_getenv, mocker, capsys):
        # Mock TickerService
        mock_service = Mock()
        mock_service.get_multiple_tickers.return_value = {
            "Gold Price": 3313.40,
            "Oil Price (WTI)": 75.50,
        }

        # Mock environment variable as None
        mock_getenv.return_value = None
        
        mocker.patch("pyproj.main.TickerService", return_value=mock_service)

        result = get_all_market_data()

        expected = {
            "Gold Price": 3313.40,
            "Oil Price (WTI)": 75.50,
        }
        assert result == expected

        # Check console output
        captured = capsys.readouterr()
        assert "Warning: NTFY_SH_ENDPOINT environment variable not set" in captured.out