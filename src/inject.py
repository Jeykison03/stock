from datetime import date

import pandas  as pd
from sqlalchemy  import text
from fetch_stocks  import StockAPI
from clean_data  import Stock_Cleaner
from data_base  import get_engine

class Stock_Ingestor:
    def __init__(self, api_key, store_url):
        self.api = StockAPI(api_key = api_key, store_url = store_url)
        self.cleaner = Stock_Cleaner()
        self.engine = get_engine()

    def ingest(self, symbol):
        raw_data = self.api.get_stock(symbol)
        if "error" in raw_data:
            print(f"Error fetching data for {symbol}: {raw_data['error']}")
            return
        
        cleaner = self.cleaner.clean_data(raw_data, symbol)

        return cleaner
    
    def save_to_db(self, cleaned_df, symbol):
        
        
        query = text("""
                INSERT INTO stock_prices (symbol, date, open, high, low, close, volume)
                VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
                ON CONFLICT (symbol, date) DO NOTHING
                """)
        
        with self.engine.connect() as conn:
            for _, row in cleaned_df.iterrows():
                data = {
            "symbol": symbol,
            "date": row['date'],
            "open": row['open'],
            "high": row['high'],
            "low": row['low'],
            "close": row['close'],
            "volume": row['volume']
            }
        with self.engine.connect() as conn:
            conn.execute(query, data)
            conn.commit()

if __name__ == "__main__":
    ingestor = Stock_Ingestor(
        api_key  = "your_key_here",
        store_url = "https://www.alphavantage.co/query"
    )
 
    df = ingestor.ingest(symbol="AAPL")
    if df is not None:
        ingestor.save_to_db(df, symbol="AAPL")