import unittest

from docker.errors import APIError, DockerException


class APIErrorTest(unittest.TestCase):
    def test_api_error_is_caught_by_dockerexception(self):
        try:
            raise APIError("this should be caught by DockerException")
        except DockerException:
            pass
