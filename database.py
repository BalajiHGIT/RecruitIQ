"""MySQL connection helper."""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        raise RuntimeError(
            "Could not connect to MySQL. Check that MySQL is running and .env credentials are correct."
        ) from exc
