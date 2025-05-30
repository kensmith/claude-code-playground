import yfinance as yf
import requests
import os
from typing import Dict, Optional


class TickerService:
    def __init__(self):
        pass

    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get the latest closing price for a given ticker symbol."""
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="1d")
            if not history.empty:
                return history["Close"].iloc[-1]
            return None
        except Exception:
            return None

    def get_multiple_tickers(
        self, symbols: Dict[str, str]
    ) -> Dict[str, Optional[float]]:
        """Get prices for multiple ticker symbols.

        Args:
            symbols: Dict mapping display names to ticker symbols

        Returns:
            Dict mapping display names to prices
        """
        result = {}
        for name, symbol in symbols.items():
            result[name] = self.get_ticker_price(symbol)
        return result


def get_all_market_data():
    """Get comprehensive market data including commodities, currencies, and indices."""
    service = TickerService()
    symbols = {
        # Commodities
        "Gold Price": "GC=F",
        "Oil Price (WTI)": "CL=F",
        # Dollar Index
        "DXY Dollar Index": "DX-Y.NYB",
        # Currency Pairs (USD vs other currencies)
        "USD/EUR": "EURUSD=X",
        "USD/JPY": "USDJPY=X",
        "USD/CNH": "USDCNH=X",
        "USD/TWD": "USDTWD=X",
        "BTC/USD": "BTC-USD",
        # Volatility Indices
        "VIX": "^VIX",
        "MOVE Index": "^MOVE",
        # Stock Indices
        "NASDAQ": "^IXIC",
    }

    prices = service.get_multiple_tickers(symbols)

    # Format all data into a single message
    message_lines = []
    for name, price in prices.items():
        if price is not None:
            if "Gold" in name or "Oil" in name:
                message_lines.append(f"{name}: ${price:.2f}")
            elif "BTC" in name:
                message_lines.append(f"{name}: ${price:,.2f}")
            elif "USD/" in name or "DXY" in name:
                message_lines.append(f"{name}: {price:.4f}")
            elif "VIX" in name or "MOVE" in name:
                message_lines.append(f"{name}: {price:.2f}")
            elif "NASDAQ" in name:
                message_lines.append(f"{name}: {price:,.2f}")
            else:
                message_lines.append(f"{name}: {price:.2f}")
        else:
            message_lines.append(f"{name}: unavailable")

    # Send notification to ntfy.sh
    message = "\n".join(message_lines)
    ntfy_endpoint = os.getenv("NTFY_SH_ENDPOINT")
    if not ntfy_endpoint:
        print("Warning: NTFY_SH_ENDPOINT environment variable not set")
        return prices
    
    try:
        response = requests.post(
            ntfy_endpoint,
            data=message,
            headers={"Title": "Market Data Update"},
        )
        if response.status_code == 200:
            print("Market data sent to ntfy.sh successfully")
        else:
            print(f"Failed to send notification: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification: {e}")

    return prices


def get_gold_and_dxy():
    """Legacy function - use get_all_market_data() instead."""
    service = TickerService()
    symbols = {"Gold Price": "GC=F", "DXY Dollar Index": "DX-Y.NYB"}
    prices = service.get_multiple_tickers(symbols)

    # Format legacy output for backwards compatibility
    message_lines = []
    for name, price in prices.items():
        if price is not None:
            if name == "Gold Price":
                message_lines.append(f"{name}: ${price:.2f}")
            else:
                message_lines.append(f"{name}: {price:.4f}")
        else:
            message_lines.append(f"{name}: unavailable")

    # Send notification to ntfy.sh
    message = "\n".join(message_lines)
    ntfy_endpoint = os.getenv("NTFY_SH_ENDPOINT")
    if not ntfy_endpoint:
        print("Warning: NTFY_SH_ENDPOINT environment variable not set")
        return prices
    
    try:
        response = requests.post(
            ntfy_endpoint,
            data=message,
            headers={"Title": "Legacy Market Data"},
        )
        if response.status_code == 200:
            print("Legacy market data sent to ntfy.sh successfully")
        else:
            print(f"Failed to send notification: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification: {e}")

    return prices


if __name__ == "__main__":
    get_all_market_data()
