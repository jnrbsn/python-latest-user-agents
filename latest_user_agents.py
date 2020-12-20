import json
import os
import random
import shutil
import threading
import time

import requests
from appdirs import user_cache_dir

_download_url = 'https://jnrbsn.github.io/user-agents/user-agents.json'

_cache_dir = user_cache_dir('jnrbsn-user-agents', 'jnrbsn')
_cache_file = os.path.join(_cache_dir, 'user-agents.json')
_last_request_time_file = os.path.join(_cache_dir, 'last-request-time.txt')

_cached_user_agents = None
_cache_lock = threading.RLock()


class LatestUserAgentsError(Exception):
    """Custom exception used by this module."""
    pass


def _download():
    with _cache_lock:
        os.makedirs(_cache_dir, mode=0o755, exist_ok=True)

        with open(_last_request_time_file, 'w') as f:
            f.write('{}\n'.format(int(time.time())))

        # Download the latest user agents
        response = requests.get(_download_url)
        response.raise_for_status()

        # Write it to the cache file
        with open(_cache_file, 'w') as f:
            f.write(response.text)

        return response.json()


def _get_last_request_time():
    with _cache_lock:
        with open(_last_request_time_file, 'r') as f:
            return int(f.read())


def _read_cache():
    with _cache_lock:
        with open(_cache_file, 'r') as f:
            return json.load(f)


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

        now = time.time()

        if os.path.isfile(_cache_file):
            cache_age = now - os.path.getmtime(_cache_file)
            if cache_age < 86400 or now - _get_last_request_time() < 3600:
                # Cache is less than a day old
                _cached_user_agents = _read_cache()
                return _cached_user_agents

            # Cache is at least a day old, and the last request
            # was over an hour ago
            try:
                _cached_user_agents = _download()
            except (requests.ConnectionError, requests.HTTPError):
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
        if os.path.isdir(_cache_dir):
            shutil.rmtree(_cache_dir)


def get_random_user_agent():
    """Get a random user agent string."""
    return random.choice(get_latest_user_agents())
