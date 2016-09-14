import unittest
import docker


class VolumesTest(unittest.TestCase):
    def tearDown(self):
        client = docker.from_env()
        for volume in client.volumes.list(filters={'name': 'dockerpytest_'}):
            volume.remove()

    def test_create_get(self):
        client = docker.from_env()
        volume = client.volumes.create(
            'dockerpytest_1',
            driver='local',
            labels={'labelkey': 'labelvalue'}
        )
        assert volume.id
        assert volume.name == 'dockerpytest_1'
        assert volume.attrs['Labels'] == {'labelkey': 'labelvalue'}

        volume = client.volumes.get(volume.id)
        assert volume.name == 'dockerpytest_1'

    def test_list_remove(self):
        client = docker.from_env()
        volume = client.volumes.create('dockerpytest_1')
        assert volume in client.volumes.list()
        assert volume in client.volumes.list(filters={'name': 'dockerpytest_'})
        assert volume not in client.volumes.list(filters={'name': 'foobar'})

        volume.remove()
        assert volume not in client.volumes.list()
