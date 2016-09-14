import unittest
import docker
from .. import helpers


class NodesTest(unittest.TestCase):
    def setUp(self):
        helpers.force_leave_swarm(docker.from_env())

    def tearDown(self):
        helpers.force_leave_swarm(docker.from_env())

    def test_list_get(self):
        client = docker.from_env()
        client.swarm.init()
        nodes = client.nodes.list()
        assert len(nodes) == 1
        assert nodes[0].attrs['Spec']['Role'] == 'manager'
        node = client.nodes.get(nodes[0].id)
        assert node.id == nodes[0].id
        assert node.attrs['Spec']['Role'] == 'manager'
