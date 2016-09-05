import unittest

import docker


class ContainerCollectionTest(unittest.TestCase):

    def test_run(self):
        client = docker.from_env()
        self.assertEqual(
            client.containers.run("alpine", "echo hello world"),
            b'hello world\n'
        )

    def test_run_detach(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 300", detach=True)
        assert container.attrs['Config']['Image'] == "alpine"
        assert container.attrs['Config']['Cmd'] == ['sleep', '300']

    def test_run_with_error(self):
        client = docker.from_env()
        with self.assertRaises(docker.errors.ContainerError) as cm:
            client.containers.run("alpine", "cat /test")
        assert cm.exception.exit_status == 1
        assert "cat /test" in str(cm.exception)
        assert "alpine" in str(cm.exception)
        assert "No such file or directory" in str(cm.exception)

    def test_get(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 300", detach=True)
        assert client.containers.get(container.id).attrs[
            'Config']['Image'] == "alpine"

    def test_list(self):
        client = docker.from_env()
        container_id = client.containers.run(
            "alpine", "sleep 300", detach=True).id
        containers = [c for c in client.containers.list() if c.id ==
                      container_id]
        assert len(containers) == 1

        container = containers[0]
        assert container.attrs['Config']['Image'] == 'alpine'

        container.kill()
        container.remove()
        assert container_id not in [c.id for c in client.containers.list()]


class ContainerTest(unittest.TestCase):

    def test_attach(self):
        pass  # TODO

    def test_commit(self):
        client = docker.from_env()
        container = client.containers.run(
            "alpine", "sh -c 'echo \"hello\" > /test'",
            detach=True
        )
        container.wait()
        image = container.commit()
        self.assertEqual(
            client.containers.run(image.id, "cat /test"),
            b"hello\n"
        )

    def test_diff(self):
        pass  # TODO

    def test_export(self):
        pass  # TODO

    def test_get_archive(self):
        pass  # TODO

    def test_kill(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 300", detach=True)
        while container.status != 'running':
            container = client.containers.get(container.id)
        assert container.status == 'running'
        container.kill()
        container = client.containers.get(container.id)
        assert container.status == 'exited'

    def test_status(self):
        pass  # TODO
