import docker
from docker.models.containers import Container
from docker.models.images import Image
import unittest

from .fake_api import FAKE_CONTAINER_ID, FAKE_IMAGE_ID
from .fake_api_client import make_fake_client


class ContainerCollectionTest(unittest.TestCase):
    def test_run(self):
        client = make_fake_client()
        out = client.containers.run(
            'alpine',
            'echo hello world',
            environment={'FOO': 'BAR'},
            working_dir='/code'
        )

        assert out == 'hello world\n'
        client.api.create_container.assert_called_with(
            'alpine',
            'echo hello world',
            environment={'FOO': 'BAR'},
            working_dir='/code'
        )
        client.api.inspect_container.assert_called_with(FAKE_CONTAINER_ID)
        client.api.start.assert_called_with(FAKE_CONTAINER_ID)
        client.api.wait.assert_called_with(FAKE_CONTAINER_ID)
        client.api.logs.assert_called_with(
            FAKE_CONTAINER_ID,
            stderr=False,
            stdout=True
        )

    def test_run_detach(self):
        client = make_fake_client()
        container = client.containers.run('alpine', 'sleep 300', detach=True)
        assert isinstance(container, Container)
        assert container.id == FAKE_CONTAINER_ID
        client.api.create_container.assert_called_with(
            'alpine',
            'sleep 300',
            detach=True
        )
        client.api.inspect_container.assert_called_with(FAKE_CONTAINER_ID)
        client.api.start.assert_called_with(FAKE_CONTAINER_ID)

    def test_run_pull(self):
        client = make_fake_client()

        # raise exception on first call, then return normal value
        class MockResponse(object):
            status_code = 404
            content = "No such image: alpine (tag: latest)"

            def json(self):
                return {"message": self.content}

        client.api.create_container.side_effect = [
            docker.errors.APIError("", MockResponse()),
            client.api.create_container.return_value
        ]

        container = client.containers.run('alpine', 'sleep 300', detach=True)

        assert container.id == FAKE_CONTAINER_ID
        client.api.pull.assert_called_with('alpine')

    def test_run_with_error(self):
        client = make_fake_client()
        client.api.logs.return_value = "some error"
        client.api.wait.return_value = 1

        with self.assertRaises(docker.errors.ContainerError) as cm:
            client.containers.run('alpine', 'echo hello world')
        assert cm.exception.exit_status == 1
        assert "some error" in str(cm.exception)

    def test_create(self):
        client = make_fake_client()
        container = client.containers.create(
            'alpine',
            'echo hello world',
            environment={'FOO': 'BAR'}
        )
        assert isinstance(container, Container)
        assert container.id == FAKE_CONTAINER_ID
        client.api.create_container.assert_called_with(
            'alpine',
            'echo hello world',
            environment={'FOO': 'BAR'}
        )
        client.api.inspect_container.assert_called_with(FAKE_CONTAINER_ID)

    def test_get(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        assert isinstance(container, Container)
        assert container.id == FAKE_CONTAINER_ID
        client.api.inspect_container.assert_called_with(FAKE_CONTAINER_ID)

    def test_list(self):
        client = make_fake_client()
        containers = client.containers.list(all=True)
        client.api.containers.assert_called_with(
            all=True,
            before=None,
            filters=None,
            limit=-1,
            since=None
        )
        client.api.inspect_container.assert_called_with(FAKE_CONTAINER_ID)
        assert len(containers) == 1
        assert isinstance(containers[0], Container)
        assert containers[0].id == FAKE_CONTAINER_ID


class ContainerTest(unittest.TestCase):
    def test_name(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        assert container.name == 'foobar'

    def test_status(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        assert container.status == "running"

    def test_attach(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.attach(stream=True)
        client.api.attach.assert_called_with(FAKE_CONTAINER_ID, stream=True)

    def test_commit(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        image = container.commit()
        client.api.commit.assert_called_with(FAKE_CONTAINER_ID)
        assert isinstance(image, Image)
        assert image.id == FAKE_IMAGE_ID

    def test_diff(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.diff()
        client.api.diff.assert_called_with(FAKE_CONTAINER_ID)

    def test_export(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.export()
        client.api.export.assert_called_with(FAKE_CONTAINER_ID)

    def test_get_archive(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.get_archive()
        client.api.get_archive.assert_called_with(FAKE_CONTAINER_ID)

    def test_kill(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.kill(signal=5)
        client.api.kill.assert_called_with(FAKE_CONTAINER_ID, signal=5)

    def test_logs(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.logs()
        client.api.logs.assert_called_with(FAKE_CONTAINER_ID)

    def test_pause(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.pause()
        client.api.pause.assert_called_with(FAKE_CONTAINER_ID)

    def test_put_archive(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.put_archive()
        client.api.put_archive.assert_called_with(FAKE_CONTAINER_ID)

    def test_remove(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.remove()
        client.api.remove_container.assert_called_with(FAKE_CONTAINER_ID)

    def test_rename(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.rename("foo")
        client.api.rename.assert_called_with(FAKE_CONTAINER_ID, "foo")

    def test_resize(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.resize(1, 2)
        client.api.resize.assert_called_with(FAKE_CONTAINER_ID, 1, 2)

    def test_restart(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.restart()
        client.api.restart.assert_called_with(FAKE_CONTAINER_ID)

    def test_start(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.start()
        client.api.start.assert_called_with(FAKE_CONTAINER_ID)

    def test_stats(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.stats()
        client.api.stats.assert_called_with(FAKE_CONTAINER_ID)

    def test_stop(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.stop()
        client.api.stop.assert_called_with(FAKE_CONTAINER_ID)

    def test_top(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.top()
        client.api.top.assert_called_with(FAKE_CONTAINER_ID)

    def test_unpause(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.unpause()
        client.api.unpause.assert_called_with(FAKE_CONTAINER_ID)

    def test_update(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.update(cpu_shares=2)
        client.api.update_container.assert_called_with(FAKE_CONTAINER_ID,
                                                       cpu_shares=2)

    def test_wait(self):
        client = make_fake_client()
        container = client.containers.get(FAKE_CONTAINER_ID)
        container.wait()
        client.api.wait.assert_called_with(FAKE_CONTAINER_ID)
