import os
import ssl
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
POOL_MAX = int(os.environ.get("PG_POOL_MAX", "10"))
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
        self._unavailable = False

    def _create_conn(self):
        if not _DATABASE_URL:
            return None
        params = _parse_url(_DATABASE_URL)
        # Supabase only has IPv6 AAAA records for the database host.
        # Vercel serverless functions need the resolved IPv6 address.
        if "supabase.co" in params.get("host", ""):
            params["port"] = 6543
            try:
                import socket
                ips = socket.getaddrinfo(params["host"], params["port"], socket.AF_INET6)
                if ips:
                    params["host"] = ips[0][4][0]
            except Exception:
                pass
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return pg8000.connect(**params, timeout=10, ssl_context=ctx)

    def getconn(self):
        if self._unavailable:
            return None
        try:
            return self._pool.get_nowait()
        except Empty:
            with self._lock:
                if self._size < self._max:
                    try:
                        conn = self._create_conn()
                    except Exception:
                        conn = None
                    if conn:
                        self._size += 1
                    else:
                        self._unavailable = True
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


def is_pg_available():
    return bool(_DATABASE_URL)


def get_pg_connection():
    if not is_pg_available():
        return None
    try:
        return PgConnection()
    except Exception:
        return None


class PgRow(dict):
    def __init__(self, cols, values):
        self._cols = cols
        data = {}
        for i, col in enumerate(cols):
            data[col] = _normalize(values[i])
        super().__init__(data)

    def __getitem__(self, key):
        if isinstance(key, int):
            col = self._cols[key]
            return super().__getitem__(col)
        return super().__getitem__(key)


class PgCursor:
    def __init__(self, pg_conn):
        self._pg_conn = pg_conn
        self._pg_cursor = pg_conn.cursor()
        self._results = []
        self.rowcount = -1
        self.description = None

    def execute(self, sql, params=None):
        if params is not None and "?" in sql:
            sql = sql.replace("?", "%s")
        self._pg_cursor.execute(sql, params or ())
        self.rowcount = self._pg_cursor.rowcount
        self.description = self._pg_cursor.description
        if self.description:
            cols = [d[0].lower() for d in self.description]
            self._results = [PgRow(cols, row) for row in self._pg_cursor.fetchall()]
        else:
            self._results = []
        return self

    def fetchone(self):
        if not self._results:
            return None
        return self._results.pop(0)

    def fetchall(self):
        result = self._results[:]
        self._results = []
        return result


class PgConnection:
    def __init__(self):
        self._conn = _pool.getconn()

    def cursor(self):
        return PgCursor(self._conn)

    def execute(self, sql, params=None):
        return self.cursor().execute(sql, params)

    def commit(self):
        if self._conn:
            self._conn.commit()

    def rollback(self):
        if self._conn:
            self._conn.rollback()

    def close(self):
        if self._conn:
            _pool.putconn(self._conn)
            self._conn = None
