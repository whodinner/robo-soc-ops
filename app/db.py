# app/db.py
import os, uuid, datetime, sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("SOC_DB_PATH", "robosoc.db")

def get_connection():
    """Create a new DB connection per call (safer for concurrency)."""
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # safer: returns dict-like rows
    return conn

@contextmanager
def db_cursor():
    """Context manager for safe cursor usage with auto-commit/rollback."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db_cursor() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            type TEXT,
            source TEXT,
            details TEXT,
            severity TEXT,
            handled_by TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS incident_audit (
            id TEXT PRIMARY KEY,
            incident_id TEXT,
            timestamp TEXT,
            action TEXT,
            details TEXT,
            operator TEXT,
            hash TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS shift_handovers (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            operator TEXT,
            notes TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )""")

def seed_demo():
    now = datetime.datetime.utcnow().isoformat()
    demo_id = str(uuid.uuid4())
    with db_cursor() as cursor:
        cursor.execute("""INSERT OR IGNORE INTO incidents
            (id, timestamp, type, source, details, severity, handled_by, latitude, longitude, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (demo_id, now, "cctv_alert", "camera1", "Unauthorized access detected",
             "HIGH", "system", 36.17, -115.14, "OPEN"))

# Initialize DB on import
init_db()
seed_demo()
