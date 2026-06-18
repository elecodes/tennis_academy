import os
import ssl
from urllib.parse import urlparse, urlencode, parse_qs

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL_READONLY")

connect_args = {}
if DATABASE_URL:
    # pg8000 doesn't support sslmode query param — handle it via connect_args
    parsed = urlparse(DATABASE_URL)
    qs = parse_qs(parsed.query)
    if "sslmode" in qs:
        sslmode = qs.pop("sslmode")[0]
        # Rebuild URL without sslmode
        query_string = urlencode(qs, doseq=True)
        DATABASE_URL = DATABASE_URL.replace(f"?{parsed.query}", "")
        if query_string:
            DATABASE_URL += f"?{query_string}"
        # sslmode=require → use SSL with default context (no cert verification)
        if sslmode == "require":
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl_context"] = ctx

    # Use pg8000 (pure Python) for Python 3.14 compatibility
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args) if DATABASE_URL else None
Session = sessionmaker(bind=engine) if engine else None


def get_supabase_db():
    if Session is None:
        return None
    return Session()
