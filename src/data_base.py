
import os
from sqlalchemy  import create_engine, text
from dotenv   import load_dotenv

load_dotenv()

def get_engine():
    db_user     = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host     = os.getenv("DB_HOST")
    db_port     = os.getenv("DB_PORT")
    db_name     = os.getenv("DB_NAME")
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)
    return engine

def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"Connected successfully!")
            print(f"PostgreSQL version: {version}")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Check your .env file — DB_HOST, DB_USER, DB_PASSWORD")


# run this file directly to test connection
if __name__ == "__main__":
    test_connection()

