import os
import sqlite3
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TursoRow(dict):
    """A row object that supports both indexing by name and index, and attribute access."""

    def __init__(self, cols, raw_values):
        self._cols = cols
        self._raw_values = raw_values
        data = {}
        for i, col in enumerate(cols):
            data[col] = self._translate_value(raw_values[i])
        super().__init__(data)

    def _translate_value(self, val):
        """Translate Turso JSON type to Python native type."""
        if not isinstance(val, dict):
            return val

        v_type = val.get("type")
        if v_type == "null":
            return None
        elif v_type == "integer":
            return int(val.get("value", 0))
        elif v_type == "float":
            return float(val.get("value", 0.0))
        elif v_type == "text":
            return val.get("value", "")
        elif v_type == "blob":
            import base64

            return base64.b64decode(val.get("base64", ""))
        return val.get("value", val)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._translate_value(self._raw_values[key])
        return super().__getitem__(key)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'TursoRow' object has no attribute '{name}'")


class TursoCursor:
    def __init__(self, connection):
        self.connection = connection
        self.last_result = None
        self.description = None

    def execute(self, sql, params=()):
        # Convert params to Turso-compatible args
        # Turso HTTP API expects a list of values or named dicts
        args = []
        for p in params:
            if isinstance(p, (int, float)):
                args.append(
                    {
                        "type": "float" if isinstance(p, float) else "integer",
                        "value": str(p),
                    }
                )
            elif p is None:
                args.append({"type": "null"})
            else:
                args.append({"type": "text", "value": str(p)})

        payload = {
            "requests": [{"type": "execute", "stmt": {"sql": sql, "args": args}}]
        }

        response = requests.post(
            self.connection.http_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self.connection.token}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        res_data = response.json()

        # Parse the nested pipeline result
        # Structure: {"results": [{"type": "ok", "response": {"type": "execute", "result": {...}}}]}
        try:
            res = res_data["results"][0]
            if res["type"] == "error":
                error_msg = res["error"]["message"]
                raise Exception(f"Turso SQL Error: {error_msg}")

            exe_res = res["response"]["result"]
            self.last_result = exe_res
            self.description = [
                (col["name"], None, None, None, None, None, None)
                for col in exe_res["cols"]
            ]
            return self
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to parse Turso response: {res_data}. Error: {e}")

    def fetchone(self):
        if not self.last_result or not self.last_result.get("rows"):
            return None
        row_values = self.last_result["rows"][0]
        cols = [col["name"] for col in self.last_result["cols"]]
        return TursoRow(cols, row_values)

    def fetchall(self):
        if not self.last_result or not self.last_result.get("rows"):
            return []
        cols = [col["name"] for col in self.last_result["cols"]]
        return [TursoRow(cols, row) for row in self.last_result["rows"]]

    @property
    def lastrowid(self):
        if self.last_result:
            return self.last_result.get("last_insert_rowid")
        return None

    @property
    def rowcount(self):
        if self.last_result:
            return self.last_result.get("affected_row_count", 0)
        return 0


class TursoConnection:
    def __init__(self, url, token):
        # Convert libsql:// to https://
        if url.startswith("libsql://"):
            self.base_url = url.replace("libsql://", "https://")
        else:
            self.base_url = url

        self.http_url = self.base_url.rstrip("/") + "/v2/pipeline"
        self.token = token
        self.row_factory = sqlite3.Row  # Placeholder

    def cursor(self):
        return TursoCursor(self)

    def execute(self, sql, params=()):
        return self.cursor().execute(sql, params)

    def commit(self):
        # Turso autocommits or handles transactions via pipeline
        pass

    def close(self):
        pass


def get_db():
    url = os.environ.get("TURSO_URL")
    token = os.environ.get("TURSO_TOKEN")

    if url and token:
        return TursoConnection(url, token)
    else:
        # Fallback to local SQLite if no Turso config
        db_path = os.path.join(os.path.dirname(__file__), "..", "academy.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
