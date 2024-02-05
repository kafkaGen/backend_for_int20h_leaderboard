import logging
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(
        database=os.getenv("DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
    )

    return conn


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("logger")

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s]: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("logfile.txt")],  # Log to the console  # Log to a file
    )

    return logger
