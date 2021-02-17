import os
import random
import shutil
import sqlite3
import threading
import time
from contextlib import contextmanager

import requests
from appdirs import user_cache_dir

_download_url = 'https://jnrbsn.github.io/user-agents/user-agents.json'

_cache_dir = user_cache_dir('jnrbsn-user-agents', 'jnrbsn')
_cache_file = os.path.join(_cache_dir, 'user-agents.sqlite')
_cache_schema = [
    """
    CREATE TABLE IF NOT EXISTS "user_agents" (
        "last_seen" INTEGER NOT NULL,
        "user_agent" TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS "user_agents_last_seen"
        ON "user_agents" ("last_seen")
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS "user_agents_user_agent"
        ON "user_agents" ("user_agent")
    """,
    """
    CREATE TABLE IF NOT EXISTS "last_download_attempt" (
        "id" INTEGER PRIMARY KEY CHECK ("id" = 0),
        "last_download_attempt" INTEGER NOT NULL
    )
    """,
]

_cached_user_agents = None
_cache_lock = threading.RLock()


class LatestUserAgentsError(Exception):
    """Custom exception used by this module."""
    pass


@contextmanager
def _cache_db_transaction(connection):
    cursor = connection.cursor()
    cursor.execute('BEGIN')
    try:
        yield cursor
        cursor.execute('COMMIT')
    except Exception:
        cursor.execute('ROLLBACK')
        raise


@contextmanager
def _cache_db_connection():
    os.makedirs(_cache_dir, mode=0o755, exist_ok=True)
    connection = sqlite3.connect(_cache_file, isolation_level=None)
    connection.execute('PRAGMA journal_mode = wal')
    connection.execute('PRAGMA synchronous = normal')
    connection.execute('PRAGMA temp_store = memory')
    connection.execute('PRAGMA foreign_keys = 1')
    connection.execute('PRAGMA cache_size = -8192')  # 8 MiB
    connection.execute('PRAGMA mmap_size = 8388608')  # 8 MiB
    try:
        with _cache_db_transaction(connection) as cursor:
            for query in _cache_schema:
                cursor.execute(query)
        yield connection
    finally:
        connection.close()


def _download():
    with _cache_lock:
        with _cache_db_connection() as connection:
            with _cache_db_transaction(connection) as cursor:
                now = int(time.time())
                # Record the time of the last download attempt
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO "last_download_attempt"
                        ("id", "last_download_attempt") VALUES (0, ?)
                    """,
                    (now,),
                )

            # Download the latest user agents
            response = requests.get(_download_url, timeout=5)
            response.raise_for_status()
            user_agents = response.json()

            with _cache_db_transaction(connection) as cursor:
                now = int(time.time())
                # Insert new user agents
                cursor.executemany(
                    """
                    INSERT OR REPLACE INTO "user_agents"
                        ("last_seen", "user_agent") VALUES (?, ?)
                    """,
                    [(now, ua) for ua in user_agents],
                )
                # Delete user agents older than 14 days
                cursor.execute(
                    'DELETE FROM "user_agents" WHERE "last_seen" < ?',
                    (now - (14 * 86400),),
                )

            return user_agents


def _get_last_request_time():
    with _cache_lock:
        with _cache_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT "last_download_attempt"
                    FROM "last_download_attempt"
                    WHERE "id" = 0
                """)
            # The one row should always be present
            return cursor.fetchone()[0]


def _get_cache_age():
    with _cache_lock:
        with _cache_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT MAX("last_seen") FROM "user_agents"')
            row = cursor.fetchone()
            if row is None or row[0] is None:
                return None
            return int(time.time() - row[0])


def _read_cache():
    with _cache_lock:
        with _cache_db_connection() as connection:
            return [
                row[0] for row in connection.execute(
                    'SELECT "user_agent" from "user_agents"')
            ]


def get_latest_user_agents():
    """Get the latest user agent strings for major browsers and OSs."""
    global _cached_user_agents

    if _cached_user_agents is not None:
        # Cached in memory
        return _cached_user_agents

    with _cache_lock:
        if _cached_user_agents is not None:
            # Another thread must have filled the cache while we were
            # waiting for the lock
            return _cached_user_agents

        cache_age = _get_cache_age()
        if cache_age is not None:
            if (cache_age < 86400
                    or time.time() - _get_last_request_time() < 3600):
                # Cache is less than a day old
                _cached_user_agents = _read_cache()
                return _cached_user_agents

            # Cache is at least a day old, and the last request
            # was over an hour ago
            try:
                _cached_user_agents = _download()
            except Exception:
                if cache_age >= 7 * 86400:
                    raise LatestUserAgentsError((
                        'User agent cache is {:.1f} days old, '
                        'and attempted update failed').format(cache_age))
                else:
                    # Just keep using the cache for now
                    _cached_user_agents = _read_cache()

            return _cached_user_agents

        _cached_user_agents = _download()
        return _cached_user_agents


def clear_user_agent_cache():
    """Clear the local cache of user agents."""
    global _cached_user_agents

    with _cache_lock:
        _cached_user_agents = None
        try:
            shutil.rmtree(_cache_dir)
        except FileNotFoundError:
            pass


def get_random_user_agent():
    """Get a random user agent string."""
    return random.choice(get_latest_user_agents())
