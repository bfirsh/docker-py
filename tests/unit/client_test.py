import datetime
import docker
import os
import unittest

from . import fake_api

try:
    from unittest import mock
except ImportError:
    import mock


class ClientTest(unittest.TestCase):

    @mock.patch('docker.api.APIClient.events')
    def test_events(self, mock_func):
        since = datetime.datetime(2016, 1, 1, 0, 0)
        mock_func.return_value = fake_api.get_fake_events()[1]
        client = docker.from_env()
        assert client.events(since=since) == mock_func.return_value
        mock_func.assert_called_with(since=since)

    @mock.patch('docker.api.APIClient.info')
    def test_info(self, mock_func):
        mock_func.return_value = fake_api.get_fake_info()[1]
        client = docker.from_env()
        assert client.info() == mock_func.return_value
        mock_func.assert_called_with()

    @mock.patch('docker.api.APIClient.ping')
    def test_ping(self, mock_func):
        mock_func.return_value = True
        client = docker.from_env()
        assert client.ping() is True
        mock_func.assert_called_with()

    @mock.patch('docker.api.APIClient.version')
    def test_version(self, mock_func):
        mock_func.return_value = fake_api.get_fake_version()[1]
        client = docker.from_env()
        assert client.version() == mock_func.return_value
        mock_func.assert_called_with()
