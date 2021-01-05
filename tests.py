import json
import os
import shutil
import time
from tempfile import mkdtemp
from threading import Thread

import pytest
import requests
from freezegun import freeze_time

import latest_user_agents
from latest_user_agents import (
    clear_user_agent_cache, get_latest_user_agents, get_random_user_agent)

__all__ = []

fake_user_agents = ['Mozilla/5.0 (Foo) Bar', 'Mozilla/5.0 (Baz) Qux']


def _items_equal(a, b):
    return len(a) == len(b) and sorted(a) == sorted(b)


@pytest.fixture(scope='function', autouse=True)
def patch_cache(monkeypatch):
    """Make all tests use a fresh cache.

    The cache directory will be a unique temporary directory for all test
    functions, and the in-memory cache will be cleared before each test.
    """
    tmp_dir = mkdtemp(prefix='latest_user_agents_test_')
    try:
        # Change cache location on disk
        monkeypatch.setattr(latest_user_agents, '_cache_dir', tmp_dir)
        monkeypatch.setattr(
            latest_user_agents, '_cache_file',
            os.path.join(tmp_dir, 'user-agents.sqlite'))

        # Clear in-memory cache
        monkeypatch.setattr(latest_user_agents, '_cached_user_agents', None)

        yield
    finally:
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)


@pytest.fixture(scope='function', autouse=True)
def patch_requests(monkeypatch):
    """Mock HTTP requests wtih fake data instead of making real requests."""
    class MockResponse(object):
        text = json.dumps(fake_user_agents, indent=4).strip() + '\n'

        @staticmethod
        def json():
            return fake_user_agents

        @staticmethod
        def raise_for_status():
            pass

    def mock_requests_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_get)


@pytest.fixture(scope='function')
def spy_download(mocker):
    """Spy on downloads of new user agent data."""
    return mocker.spy(latest_user_agents, '_download')


@pytest.fixture(scope='function')
def spy_read_cache(mocker):
    """Spy on reads of the cache file."""
    return mocker.spy(latest_user_agents, '_read_cache')


@pytest.fixture(name='clear_in_memory_cache', scope='function')
def clear_in_memory_cache_fixture(monkeypatch):
    """Return a function that can clear the in-memory cache."""
    def fixture():
        monkeypatch.setattr(latest_user_agents, '_cached_user_agents', None)
    return fixture


@pytest.mark.parametrize(
    ('test_func', 'assertion'),
    (
        (get_latest_user_agents, lambda x: _items_equal(x, fake_user_agents)),
        (get_random_user_agent, lambda x: x in fake_user_agents),
    ),
)
def test_latest_user_agents(
        test_func, assertion, spy_download, spy_read_cache,
        clear_in_memory_cache):
    """Test basic/normal usage of main functions."""
    # This should download new data
    assert assertion(test_func())
    spy_download.assert_called_once()

    spy_download.reset_mock()
    clear_in_memory_cache()

    # This should NOT download new data, but read the cache on-disk since
    # we cleared the in-memory cache above
    assert assertion(test_func())
    spy_download.assert_not_called()
    spy_read_cache.assert_called_once()

    spy_download.reset_mock()
    spy_read_cache.reset_mock()

    # This should neither download new data nor read the cache because
    # it hits the in-memory cache
    assert assertion(test_func())
    spy_download.assert_not_called()
    spy_read_cache.assert_not_called()

    spy_download.reset_mock()
    clear_user_agent_cache()

    # This should download new data again since we cleared all the cache above
    assert assertion(test_func())
    spy_download.assert_called_once()


def test_expired_cache(spy_download, clear_in_memory_cache):
    """Test normal cache expiration."""
    with freeze_time() as frozen_time:
        # This should download new data
        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_called_once()

        spy_download.reset_mock()
        clear_in_memory_cache()

        frozen_time.tick(25 * 3600)

        # This should download new data again since the cache expired
        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_called_once()


def test_double_clear_cache():
    """Test that clearing the cache multiple times doesn't cause errors."""
    clear_user_agent_cache()
    clear_user_agent_cache()


def test_download_error(
        monkeypatch, spy_download, spy_read_cache, clear_in_memory_cache):
    """Test cache expiration when we're unable to download new data."""
    with freeze_time() as frozen_time:
        # This should download new data
        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_called_once()

        spy_download.reset_mock()
        clear_in_memory_cache()

        frozen_time.tick(25 * 3600)

        # Mock a download failure
        class MockResponse(object):
            @staticmethod
            def raise_for_status():
                raise requests.ConnectionError()

        def mock_requests_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(requests, 'get', mock_requests_get)

        # This will attempt to download new data but end up reading the cache
        assert _items_equal(get_latest_user_agents(), fake_user_agents)
        spy_download.assert_called_once()
        assert isinstance(spy_download.spy_exception, requests.ConnectionError)
        spy_read_cache.assert_called_once()

        spy_download.reset_mock()
        spy_read_cache.reset_mock()
        clear_in_memory_cache()

        # This should NOT download new data, but read the cache on-disk since
        # we cleared the in-memory cache above
        assert _items_equal(get_latest_user_agents(), fake_user_agents)
        spy_download.assert_not_called()
        spy_read_cache.assert_called_once()

        spy_download.reset_mock()
        spy_read_cache.reset_mock()
        clear_in_memory_cache()

        frozen_time.tick(7 * 86400)

        # Since the cache is too old, this will raise an exception
        with pytest.raises(latest_user_agents.LatestUserAgentsError):
            get_latest_user_agents()


def test_racing_locks(spy_download, spy_read_cache):
    """Test multiple threads racing to get a lock."""
    # Acquire the lock
    latest_user_agents._cache_lock.acquire()

    # Start another thread and give it enough time to block while trying
    # to acquire the lock itself
    thread = Thread(target=get_latest_user_agents)
    thread.start()
    time.sleep(1)

    # Fill the cache while the other thread is waiting for the lock
    assert get_latest_user_agents() == fake_user_agents
    spy_download.reset_mock()
    spy_read_cache.reset_mock()

    # Release the lock and check that the other thread used the cache
    # that we just filled
    latest_user_agents._cache_lock.release()
    thread.join()
    spy_download.assert_not_called()
    spy_read_cache.assert_not_called()
