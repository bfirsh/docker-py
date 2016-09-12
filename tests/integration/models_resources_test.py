import unittest

import docker


class ModelTest(unittest.TestCase):

    def test_reload(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 300", detach=True)
        first_started_at = container.attrs['State']['StartedAt']
        container.kill()
        container.start()
        assert container.attrs['State']['StartedAt'] == first_started_at
        container.reload()
        assert container.attrs['State']['StartedAt'] != first_started_at
