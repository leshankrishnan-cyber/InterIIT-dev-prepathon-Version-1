import os
import psycopg

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "constants"),
    "user": os.getenv("DB_USER", "rca"),
    "password": os.getenv("DB_PASSWORD", "rca_password")
}

def get_connection():
    return psycopg.connect(**DB_CONFIG)
