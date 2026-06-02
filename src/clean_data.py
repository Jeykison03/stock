import pandas as pd 
from fetch_stocks import StockAPI

class Stock_Cleaner:
    def __init__(self):
        self.column_rename = {
            "1. open":   "open",
            "2. high":   "high",
            "3. low":    "low",
            "4. close":  "close",
            "5. volume": "volume"
        }
 

    def clean_data(self, raw_data, symbol):
        if 'error' in raw_data:
            print(f"Error in raw data: {raw_data['error']}")
            return None
        
        time_series = raw_data.get("Time Series (Daily)")
        df = pd.DataFrame.from_dict(time_series, orient ='index')  # orient="index" means each date key becomes a ROW
        df = df.reset_index().rename(columns={'index': 'date'})
        df = df.rename(columns = self.column_rename)
        df = df.astype({
            "date": 'datetime64[ns]',
            "open": 'float',
            "high": 'float',
            "low": 'float',
            "close": 'float',
            "volume": 'int'
        })
        df['symbol'] = symbol
        df = df.dropna()
        df = df[df['volume'] > 0]
        df = df.sort_values(by="date", ascending=False).reset_index(drop=True)
        return df
    
    def print_cleaned_data(self, df):
        print("\n" + "="*50)
        print("CLEANED DATAFRAME")
        print("="*50)
 
        print(f"\nShape: {df.shape[0]} rows × {df.shape[1]} columns")
 
        print("\nColumn names and data types:")
        print("-"*35)
        print(df.dtypes)
 
        print("\nFirst 3 rows:")
        print("-"*35)
        print(df.head(1).to_string(index=False))
 
        print("\nLast 3 rows:")
        print("-"*35)
        print(df.tail(1).to_string(index=False))
 
        print("\nAny missing values?")
        print("-"*35)
        print(df.isnull().sum())
 
        print("="*50)

if __name__ == "__main__":
    api = StockAPI(
        api_key  = "AR4DA9MHJ48B6NG1",
        store_url = "https://www.alphavantage.co/query"
    )
    raw_data = api.get_stock(symbol="AAPL")
    cleaner = Stock_Cleaner()
    cleaned_df = cleaner.clean_data(raw_data, symbol='AAPL')
    cleaner.print_cleaned_data(cleaned_df)
