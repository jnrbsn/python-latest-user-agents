import json
import os
import random
import time
from typing import List, Optional

import requests
from appdirs import user_cache_dir

_download_url: str = 'https://jnrbsn.github.io/user-agents/user-agents.json'
_cache_file: str = os.path.join(
    user_cache_dir('jnrbsn-user-agents', 'jnrbsn'),
    'user-agents.json')
_cached_user_agents: Optional[List[str]] = None


def get_latest_user_agents() -> List[str]:
    """Get the latest user agent strings for major browsers and OSs"""
    global _cached_user_agents

    if _cached_user_agents is not None:
        # Cached in memory
        return _cached_user_agents

    if (os.path.isfile(_cache_file) and
            time.time() - os.path.getmtime(_cache_file) < 86400):
        # Cache file is less than a day old
        with open(_cache_file, 'r') as f:
            _cached_user_agents = json.load(f)
            return _cached_user_agents

    # Download the latest user agents
    response = requests.get(_download_url)
    response.raise_for_status()

    # Write it to the cache file
    os.makedirs(os.path.dirname(_cache_file), mode=0o755, exist_ok=True)
    with open(_cache_file, 'w') as f:
        f.write(response.text)

    _cached_user_agents = response.json()
    return _cached_user_agents


def clear_user_agent_cache() -> None:
    """Clear the local cache of user agents"""
    global _cached_user_agents
    _cached_user_agents = None
    os.remove(_cache_file)


def get_random_user_agent() -> str:
    """Get a random user agent string"""
    return random.choice(get_latest_user_agents())
