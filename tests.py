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


@pytest.fixture(scope='function', autouse=True)
def patch_cache(monkeypatch):
    tmp_dir = mkdtemp(prefix='latest_user_agents_test_')
    try:
        monkeypatch.setattr(latest_user_agents, '_cache_dir', tmp_dir)
        monkeypatch.setattr(
            latest_user_agents, '_cache_file',
            os.path.join(tmp_dir, 'user-agents.json'))
        monkeypatch.setattr(
            latest_user_agents, '_last_request_time_file',
            os.path.join(tmp_dir, 'last-request-time.txt'))
        monkeypatch.setattr(latest_user_agents, '_cached_user_agents', None)
        yield
    finally:
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)


@pytest.fixture(scope='function', autouse=True)
def patch_requests(monkeypatch):
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
def patch_requests_failure(monkeypatch):
    class MockResponse(object):
        @staticmethod
        def raise_for_status():
            raise requests.ConnectionError()

    def mock_requests_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_requests_get)


@pytest.fixture(scope='function')
def spy_download(mocker):
    return mocker.spy(latest_user_agents, '_download')


@pytest.fixture(scope='function')
def spy_read_cache(mocker):
    return mocker.spy(latest_user_agents, '_read_cache')


@pytest.fixture(name='clear_memory_cache', scope='function')
def clear_memory_cache_fixture(monkeypatch):
    def fixture():
        monkeypatch.setattr(latest_user_agents, '_cached_user_agents', None)
    return fixture


def test_latest_user_agents(spy_download, spy_read_cache, clear_memory_cache):
    assert get_latest_user_agents() == fake_user_agents
    spy_download.assert_called_once()

    spy_download.reset_mock()
    clear_memory_cache()

    assert get_latest_user_agents() == fake_user_agents
    spy_download.assert_not_called()
    spy_read_cache.assert_called_once()

    spy_download.reset_mock()
    spy_read_cache.reset_mock()

    assert get_latest_user_agents() == fake_user_agents
    spy_download.assert_not_called()
    spy_read_cache.assert_not_called()

    spy_download.reset_mock()
    clear_user_agent_cache()

    assert get_latest_user_agents() == fake_user_agents
    spy_download.assert_called_once()


def test_random_user_agent(spy_download, spy_read_cache, clear_memory_cache):
    assert get_random_user_agent() in fake_user_agents
    spy_download.assert_called_once()

    spy_download.reset_mock()
    clear_memory_cache()

    assert get_random_user_agent() in fake_user_agents
    spy_download.assert_not_called()
    spy_read_cache.assert_called_once()

    spy_download.reset_mock()
    spy_read_cache.reset_mock()

    assert get_random_user_agent() in fake_user_agents
    spy_download.assert_not_called()
    spy_read_cache.assert_not_called()

    spy_download.reset_mock()
    clear_user_agent_cache()

    assert get_random_user_agent() in fake_user_agents
    spy_download.assert_called_once()


def test_expired_cache(spy_download, clear_memory_cache):
    with freeze_time() as frozen_time:
        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_called_once()

        spy_download.reset_mock()
        clear_memory_cache()

        frozen_time.tick(25 * 3600)

        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_called_once()


def test_download_error(
        monkeypatch, spy_download, spy_read_cache, clear_memory_cache):
    with freeze_time() as frozen_time:
        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_called_once()

        spy_download.reset_mock()
        clear_memory_cache()

        frozen_time.tick(25 * 3600)

        class MockResponse(object):
            @staticmethod
            def raise_for_status():
                raise requests.ConnectionError()

        def mock_requests_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(requests, 'get', mock_requests_get)

        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_called_once()
        spy_read_cache.assert_called_once()

        spy_download.reset_mock()
        spy_read_cache.reset_mock()
        clear_memory_cache()

        assert get_latest_user_agents() == fake_user_agents
        spy_download.assert_not_called()
        spy_read_cache.assert_called_once()

        spy_download.reset_mock()
        spy_read_cache.reset_mock()
        clear_memory_cache()

        frozen_time.tick(7 * 86400)

        with pytest.raises(latest_user_agents.LatestUserAgentsError):
            get_latest_user_agents()


def test_racing_locks(spy_download, spy_read_cache):
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
