import requests
import json


class StockAPI:
    def __init__(self, api_key, store_url):
        self.api_key = api_key
        self.store_url = store_url
        
        
    def get_stock(self,symbol,interval='5min'):
        url = self.store_url
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key
        }

        response = requests.get(url, params=params)
        
        

        if response.status_code != 200:
           return {"error": f"HTTP error {response.status_code}"}
        
        data  = response.json()
        
         
        if 'Error Message' in data:
            return {"error": data['Error Message']}
        if 'Information' in data:
            return {"error": data['Information']}
        return data
        
    def print_stock(self, data, symbol, rows= 20):
        if data is None:
            print("No data to display.")
            return
        if 'error' in data:
            print(f"Error from API: {data['error']}")
            return
        time_series = data["Time Series (Daily)"]
        print(f"\nSample data for {symbol} (first {rows} rows):")
        print("-" * 45)

        count = 0
        for time, values in list(time_series.items()):
            print(f"Time: {time}")
            for key, value in values.items():
                print(f"  {key}: {value}")
            count += 1
            if count >= rows:
                break

if __name__ == "__main__":
    stock = StockAPI(api_key ='AR4DA9MHJ48B6NG1', store_url='https://www.alphavantage.co/query')
    data =stock.get_stock(symbol='AAPL')
    stock.print_stock(data, symbol='AAPL')
