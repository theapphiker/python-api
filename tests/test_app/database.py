import os
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv
import pytest

load_dotenv()
db_uri = os.getenv('URI')

# Initialize the pool but don't open it yet
# Using a pool prevents "Connection busy" errors
pool = ConnectionPool(conninfo=db_uri, open=False) 

def get_db():
    # Context manager automatically returns the connection to the pool when done
    with pool.connection() as conn:
        # We set dict_row here so every query returns a dictionary
        with conn.cursor(row_factory=dict_row) as cursor:
            yield cursor, conn

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Open the pool before tests
    pool.open()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""TRUNCATE TABLE dev.users, dev.posts, dev.votes CASCADE;""")
            conn.commit()
    yield pool
    # Close the pool after all tests
    pool.close()

@pytest.fixture
def client(setup_database):
    from app import main
    from fastapi.testclient import TestClient
    yield TestClient(main.app)