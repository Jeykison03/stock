from datetime import date

import pandas  as pd
from sqlalchemy  import text
from fetch_stocks  import StockAPI
from clean_data  import Stock_Cleaner
from data_base  import get_engine

SYMBOLS = [ "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA" ]

class Stock_Ingestor:
    def __init__(self, api_key, store_url):
        self.api = StockAPI(api_key = api_key, store_url = store_url)
        self.cleaner = Stock_Cleaner()
        self.engine = get_engine()

    def ingest(self, symbol):
        raw_data = self.api.get_stock(symbol)
        if "error" in raw_data:
            print(f"Error fetching data for {symbol}: {raw_data['error']}")
            return None, 0
        
        cleaner = self.cleaner.clean_data(raw_data, symbol)
        raw_saved = self.save_to_db(cleaner, symbol)
        print(f"Data for {symbol} ingested successfully!")
    

        return cleaner,raw_saved
    

    def inject_all(self, symbols):
        results = []
        for symbol in symbols:
            print(f"\nIngesting data for {symbol}...")
            cleaner, raw_saved = self.ingest(symbol)
            results.append({
                "symbol":     symbol,
                "rows_saved": raw_saved,
                "status":     "success" if cleaner is not None else "failed"
            })

        self._print_summary(results)
 
        return results
    
    def _print_summary(self, results):
        """
        Prints a clean summary table after all stocks are processed.
        """
 
        print("\n" + "=" * 45)
        print("PIPELINE SUMMARY")
        print("=" * 45)
        print(f"{'Symbol':<10} {'Rows Saved':<15} {'Status'}")
        print("-" * 45)
 
        total_rows = 0
        for r in results:
            print(f"{r['symbol']:<10} {r['rows_saved']:<15} {r['status']}")
            total_rows += r["rows_saved"]
 
        print("-" * 45)
        print(f"{'TOTAL':<10} {total_rows:<15}")
        print("=" * 45)
    
    def save_to_db(self, cleaned_df, symbol):
        rows_inserted = 0
        
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
                result = conn.execute(query, data)
                rows_inserted += result.rowcount
                
                    
            conn.commit()
        return rows_inserted
    

if __name__ == "__main__":
    ingestor = Stock_Ingestor(
        api_key  = "your_key_here",
        store_url = "https://www.alphavantage.co/query"
    )
 
    ingestor.inject_all(symbols=SYMBOLS)
    