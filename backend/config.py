import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Oracle DB connection
    # Format: oracle+oracledb://user:password@host:port/?service_name=SERVICENAME
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///dev.db"  # SQLite fallback for development
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQL_DEBUG", "false").lower() == "true"
