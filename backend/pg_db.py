import os
import pg8000
import datetime
from decimal import Decimal
from queue import Queue, Empty
from threading import Lock
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


def _normalize(val):
    if isinstance(val, (datetime.time, datetime.date, datetime.datetime)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    return val


def _normalize_row(row):
    return {k: _normalize(v) for k, v in row.items()}


POOL_MIN = int(os.environ.get("PG_POOL_MIN", "2"))
POOL_MAX = int(os.environ.get("PG_POOL_MAX", "6"))
_DATABASE_URL = os.environ.get("DATABASE_URL")


def _parse_url(url):
    parts = url.replace("postgresql://", "").replace("postgres://", "")
    user_pw, rest = parts.split("@", 1)
    user, pw = user_pw.split(":", 1)
    host_port, db = rest.split("/", 1)
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 5432
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": pw,
        "database": db,
    }


class _ConnectionPool:
    def __init__(self):
        self._lock = Lock()
        self._pool = Queue()
        self._size = 0
        self._max = POOL_MAX

    def _create_conn(self):
        if not _DATABASE_URL:
            return None
        params = _parse_url(_DATABASE_URL)
        return pg8000.connect(**params, timeout=5)

    def getconn(self):
        try:
            return self._pool.get_nowait()
        except Empty:
            with self._lock:
                if self._size < self._max:
                    conn = self._create_conn()
                    if conn:
                        self._size += 1
                    return conn
            return self._pool.get(timeout=5)

    def putconn(self, conn):
        self._pool.put(conn)

    def closeall(self):
        while True:
            try:
                self._pool.get_nowait().close()
            except Empty:
                break
        self._size = 0


_pool = _ConnectionPool()


@contextmanager
def get_pg():
    conn = _pool.getconn()
    if conn is None:
        yield None
        return
    try:
        yield conn
    except Exception:
        conn.close()
        with _pool._lock:
            _pool._size -= 1
        raise
    finally:
        _pool.putconn(conn)


def pg_query(sql, params=None):
    with get_pg() as conn:
        if conn is None:
            return None
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or ())
            if sql.strip().upper().startswith("SELECT") or "RETURNING" in sql.upper():
                cols = [d[0].lower() for d in cursor.description]
                rows = cursor.fetchall()
                return [_normalize_row(dict(zip(cols, row))) for row in rows]
            conn.commit()
            return cursor.rowcount
        except Exception:
            conn.rollback()
            raise


def pg_insert(sql, params=None):
    rows = pg_query(sql, params)
    return rows


def pg_close_all():
    _pool.closeall()
