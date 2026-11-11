import os
import sys
import json
import mysql.connector as m
from mysql.connector import Error

conn = None

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_db_config():
    config = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "password",
        "database": "LibPro"
    }

    config_path = os.path.join(get_base_dir(), "db_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    config.update(loaded)
        except Exception as e:
            print(f"Warning: Could not read {config_path}: {e}")

    # Environment variables override config file if present
    config["host"] = os.getenv("LIBPRO_DB_HOST", os.getenv("DB_HOST", config["host"]))
    config["user"] = os.getenv("LIBPRO_DB_USER", os.getenv("DB_USER", config["user"]))
    config["password"] = os.getenv("LIBPRO_DB_PASS", os.getenv("DB_PASSWORD", os.getenv("DB_PASS", config["password"])))
    config["database"] = os.getenv("LIBPRO_DB_NAME", os.getenv("DB_NAME", config["database"]))

    port_env = os.getenv("LIBPRO_DB_PORT", os.getenv("DB_PORT"))
    if port_env:
        try:
            config["port"] = int(port_env)
        except ValueError:
            pass

    return config

def get_connection():
    global conn
    try:
        if conn is not None and conn.is_connected():
            try:
                conn.ping(reconnect=True, attempts=2, delay=1)
                return conn
            except Exception:
                pass

        cfg = load_db_config()
        conn = m.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            passwd=cfg["password"],
            db=cfg["database"]
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

try:
    conn = get_connection()
except Exception:
    conn = None

def fAll(query, params=None):
    c = get_connection()
    if not c:
        return []
    cur = c.cursor(buffered=True)
    try:
        cur.execute(query, params or ())
        rows = cur.fetchall()
        return rows if rows is not None else []
    except Error as e:
        print(f"Error fetching all data: {e}")
        return []
    finally:
        cur.close()

def fOne(query, params=None):
    c = get_connection()
    if not c:
        return None
    cur = c.cursor(buffered=True)
    try:
        cur.execute(query, params or ())
        return cur.fetchone()
    except Error as e:
        print(f"Error fetching one row: {e}")
        return None
    finally:
        cur.close()

def fMany(query, size, params=None):
    c = get_connection()
    if not c:
        return []
    cur = c.cursor(buffered=True)
    try:
        cur.execute(query, params or ())
        rows = cur.fetchmany(size)
        return rows if rows is not None else []
    except Error as e:
        print(f"Error fetching many rows: {e}")
        return []
    finally:
        cur.close()

def execQy(query, params=None):
    c = get_connection()
    if not c:
        return False
    cur = c.cursor()
    try:
        cur.execute(query, params or ())
        c.commit()
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        try:
            c.rollback()
        except Exception:
            pass
        return False
    finally:
        cur.close()

def closeCon():
    global conn
    if conn is not None:
        try:
            conn.close()
        except Error as e:
            print(f"Error closing connection: {e}")
        finally:
            conn = None
