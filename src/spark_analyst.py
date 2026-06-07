import os
from dotenv             import load_dotenv
from pyspark.sql        import SparkSession
from pyspark.sql        import functions as F
from pyspark.sql.window import Window

from spark_read import get_spark_session, get_jdbc_config, ROOT_DIR, stock_reader


 
load_dotenv()


class spark_transform:
    
    def read_raw(self):

        return stock_reader(project_root=ROOT_DIR).read_table("stock_prices")
    
    def add_moving_average(self, df):
        
        print("\nStep 2 — Calculating moving averages...")
        base_window = Window.partitionBy("symbol").orderBy("date")

        window_5d = base_window.rowsBetween(-4, 0)
        window_20d = base_window.rowsBetween(-19, 0)

        df = df.withColumn("Sma_5d",F.round(F.avg("close").over(window_5d), 4))
        df = df.withColumn("Sma_20d", F.round(F.avg("close").over(window_20d), 4))
        print("  Sma_5d and Sma_20d columns added")
        return df


    def add_daily_return(self, df):
        print("\nStep 3 — Calculating daily returns...")
        lag_window = Window.partitionBy("symbol").orderBy("date")

        prev_close = F.lag("close", 1).over(lag_window)
        df = df.withColumn("daily_return", F.round((F.col("close") - prev_close) / prev_close * 100, 4))
        print("  daily_return column added")
        return df
    

    def add_daily_range(self, df):
        print("\nStep 4 — Calculating daily range...")

        df = df.withColumn("daily_range", F.round(F.col("high") - F.col("low"), 4))

        print("  daily_range column added")
        return df
    


    def add_signal(self, df):
        print("\nStep 5 — Adding buy/sell signal...")
        df = df.withColumn(
            "signal",
            F.when
                (F.col("Sma_5d") > F.col("Sma_20d"), "BUY")
                .when(F.col("Sma_5d") < F.col("Sma_20d"), "SELL")
                .otherwise("HOLD")

            )
        
        print("  signal column added")
        return df
    

    def rsi(self, df, period=14):
        print(f"\nCalculating RSI with period = {period}...")
        window_spec = Window.partitionBy("symbol").orderBy("date").rowsBetween(-period, -1)

        gain = F.when(F.col("daily_return") > 0, F.col("daily_return")).otherwise(0)
        loss = F.when(F.col("daily_return") < 0, -F.col("daily_return")).otherwise(0)

        avg_gain = F.avg(gain).over(window_spec)
        avg_loss = F.avg(loss).over(window_spec)

        rs = F.when(avg_loss == 0, None).otherwise(avg_gain / avg_loss)

        rsi = F.when(rs.isNull(), 100).otherwise(100 - (100 / (1 + rs)))

        df = df.withColumn(f"RSI_{period}d", F.round(rsi, 4))
        print(f"  RSI_{period}d column added")
        return df
    
    def macd(self, df, short_period=12, long_period=26):

        print(f"\nCalculating MACD ({short_period}, {long_period})...")

        w = Window.partitionBy("symbol").orderBy("date")

    
        ema_short = F.avg("close").over(w.rowsBetween(-(short_period - 1), 0))
        ema_long = F.avg("close").over(w.rowsBetween(-(long_period - 1), 0))

    
        macd_line = ema_short - ema_long

        df = df.withColumn(
            "macd",
            F.round(macd_line, 4)
        )

        print("  macd column added")

        return df
    
    def run(self):
        print("=" * 50)
        print("SPARK TRANSFORM PIPELINE STARTING")
        print("=" * 50)
 
        # run all steps in order
        df = self.read_raw()
        df = self.add_moving_average(df)
        df = self.add_daily_return(df)
        df = self.add_daily_range(df)
        df = self.add_signal(df)
        df = self.rsi(df)
        df = self.macd(df)

        print("\n" + "=" * 50)
        print("SPARK TRANSFORM COMPLETE")
        print("gold_stock_metrics is ready for the dashboard")
        print("=" * 50)

        df.show(truncate = False)
        return df
        # show sample before writing
        
 
        # write to gold table
        
 
        

if __name__ == "__main__":
    
    transformer = spark_transform()
    
    transformer.run()

 