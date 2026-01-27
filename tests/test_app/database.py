import psycopg
from psycopg.rows import dict_row
import time
import os
from dotenv import load_dotenv

def get_db_connection():
    """
    Attempts to connect to the database. 
    Retries every 2 seconds if the connection fails.
    """
    while True:
        load_dotenv()
        db_uri = os.getenv('URI')
        try:
            # Note: In production, use environment variables for these credentials!
            conn = psycopg.connect(
                db_uri,
                row_factory=dict_row
            )
            print("Database connection was successful!")
            return conn
        except Exception as error:
            print('Connecting to database failed')
            print('Error: ', error)
            time.sleep(2)

# Initialize the connection instance
conn = get_db_connection()