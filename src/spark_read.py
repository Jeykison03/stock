import os
import sys
from dotenv import load_dotenv
from pyspark.sql import SparkSession

# Find the absolute project root folder dynamically
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Force look for .env file at the project root directly
dotenv_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)

# ============================================================
# FORCE WINDOWS ENVIRONMENT PATHS FOR PYSPARK
# ============================================================
os.environ["PYSPARK_PYTHON"] = r"C:\Python314\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Python314\python.exe"
os.environ["HADOOP_HOME"] = r"C:\hadoop"
# ============================================================

def get_spark_session(project_root):
    """Creates a Spark Session, passing the root path cleanly."""
    jdbc_jar = os.path.join(project_root, "drivers", "postgresql-42.7.11.jar")

    print(f"\n[DEBUG] Checking Driver Path: {jdbc_jar}")
    print(f"[DEBUG] File exists locally? {os.path.exists(jdbc_jar)}")

    spark = (SparkSession.builder
        .appName("StockPipeline")
        .master("local[*]") # Restored local[*] to allow proper multithreading computation
        .config("spark.jars", jdbc_jar)
        .config("spark.driver.extraClassPath", jdbc_jar) 
        .config("spark.executor.extraClassPath", jdbc_jar)
        .config("spark.driver.memory", "2g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def get_jdbc_config():
    # Fallback strings ensure these parameters are never None type
    db_host     = str(os.getenv("DB_HOST", "localhost"))
    db_port     = str(os.getenv("DB_PORT", "5432"))
    db_name     = str(os.getenv("DB_NAME", "stock_db"))
    db_user     = str(os.getenv("DB_USER", "postgres"))
    db_password = str(os.getenv("DB_PASSWORD", "Jeykison"))

    jdbc_url = f"jdbc:postgresql://{db_host}:{db_port}/{db_name}"
    
    print(f"[DEBUG] Target JDBC URL: {jdbc_url}")
    print(f"[DEBUG] Authenticating User: {db_user}")

    properties = {
        "user":     db_user,
        "password": db_password,
        "driver":   "org.postgresql.Driver"
    }
    return jdbc_url, properties

class stock_reader:
    def __init__(self, project_root):
        self.spark = get_spark_session(project_root)
        self.jdbc_url, self.properties = get_jdbc_config()

    def read_table(self, table_name):
        print(f"\nReading full table: {table_name}")
        df = (
            self.spark.read
            .format("jdbc") # Explicitly tells Spark to look for a JDBC format setup
            .option("url", self.jdbc_url)
            .option("dbtable", table_name)
            .option("user", self.properties["user"])
            .option("password", self.properties["password"])
            .option("driver", self.properties["driver"])
            .load()
        )
        return df
    
    def read_filtered(self, symbol):
        print(f"\nReading filtered data for symbol: {symbol}")
        query = f"(SELECT * FROM stock_prices WHERE symbol = '{symbol}') AS stock_data"
        df = (
            self.spark.read
            .format("jdbc")
            .option("url", self.jdbc_url)
            .option("dbtable", query)
            .option("user", self.properties["user"])
            .option("password", self.properties["password"])
            .option("driver", self.properties["driver"])
            .load()
        )
        return df
    
    def print_info(self, df, label="DataFrame"):
        print("\n" + "=" * 50)
        print(f"SPARK DATAFRAME — {label}")
        print("=" * 50)
        print(f"\nTotal rows: {df.count()}")
        df.show(90, truncate=False)


if __name__ == "__main__":
    reader = stock_reader(project_root=ROOT_DIR)
    
    # 1. Read entire database contents
    df_all = reader.read_table("stock_prices")
    reader.print_info(df_all, label="ALL STOCKS")
    
    # 2. Read single target component
    df_aapl = reader.read_filtered(symbol="AAPL")
    reader.print_info(df_aapl, label="AAPL ONLY")
    
    print("\nPart 6 complete — PySpark successfully read data from PostgreSQL!")