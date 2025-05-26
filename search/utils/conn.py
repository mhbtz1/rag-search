import os
import psycopg2
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

def spawn_connection():
    conn = psycopg2.connect(
        dbname=os.environ["dbname"],
        user=os.environ["user"],
        password=os.environ["password"],
        host=os.environ["host"],
        port=os.environ["port"]
    )
    return conn