import yfinance as yf
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
                return history['Close'].iloc[-1]
            return None
        except Exception:
            return None
    
    def get_multiple_tickers(self, symbols: Dict[str, str]) -> Dict[str, Optional[float]]:
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


def get_gold_and_dxy():
    """Get gold price and DXY dollar index using the TickerService."""
    service = TickerService()
    symbols = {
        "Gold Price": "GC=F",
        "DXY Dollar Index": "DX-Y.NYB"
    }
    
    prices = service.get_multiple_tickers(symbols)
    
    for name, price in prices.items():
        if price is not None:
            if name == "Gold Price":
                print(f"{name} (GC=F): ${price:.2f}")
            else:
                print(f"{name}: {price:.2f}")
        else:
            print(f"{name}: unavailable")
    
    return prices


if __name__ == "__main__":
    get_gold_and_dxy()
