import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

server = os.getenv("MSSQL_SERVER")
database = os.getenv("MSSQL_DATABASE")
username = os.getenv("MSSQL_USER")
password = os.getenv("MSSQL_PASSWORD")
driver = 'ODBC Driver 17 for SQL Server'

connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver.replace(' ', '+')}"

try:
    engine = create_engine(connection_string, connect_args={'timeout': 10})
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {str(e)}")

Session = sessionmaker(bind=engine)