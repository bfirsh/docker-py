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
        client = docker.from_env()
        container = client.containers.run("alpine", "touch /test", detach=True)
        container.wait()
        assert container.diff() == [{'Path': '/test', 'Kind': 1}]

    def test_exec_run(self):
        client = docker.from_env()
        container = client.containers.run(
            "alpine", "sh -c 'echo \"hello\" > /test; sleep 60'", detach=True
        )
        assert container.exec_run("cat /test") == b"hello\n"

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

    def test_logs(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "echo hello world",
                                          detach=True)
        container.wait()
        assert container.logs() == b"hello world\n"

    def test_pause(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 300", detach=True)
        container.pause()
        container = client.containers.get(container.id)
        assert container.status == "paused"
        container.unpause()
        container = client.containers.get(container.id)
        assert container.status == "running"

    def test_put_archive(self):
        # TODO
        pass

    def test_remove(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "echo hello", detach=True)
        assert container.id in [c.id for c in client.containers.list(all=True)]
        container.remove()
        containers = client.containers.list(all=True)
        assert container.id not in [c.id for c in containers]

    def test_rename(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "echo hello", name="test1",
                                          detach=True)
        assert container.name == "test1"
        container.rename("test2")
        container = client.containers.get(container.id)
        assert container.name == "test2"
        container.remove(force=True)

    def test_resize(self):
        # TODO
        pass

    def test_restart(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 100", detach=True)
        first_started_at = container.attrs['State']['StartedAt']
        container.restart()
        container = client.containers.get(container.id)
        second_started_at = container.attrs['State']['StartedAt']
        assert first_started_at != second_started_at

    def test_start(self):
        client = docker.from_env()
        container = client.containers.create("alpine", "sleep 50", detach=True)
        assert container.status == "created"
        container.start()
        container = client.containers.get(container.id)
        assert container.status == "running"

    def test_stats(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 100", detach=True)
        stats = container.stats(stream=False)
        for key in ['read', 'networks', 'precpu_stats', 'cpu_stats',
                    'memory_stats', 'blkio_stats']:
            assert key in stats

    def test_stop(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 100", detach=True)
        assert container.status in ("running", "created")
        container.stop()
        container = client.containers.get(container.id)
        assert container.status == "exited"

    def test_top(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 60", detach=True)
        top = container.top()
        assert len(top['Processes']) == 1
        assert 'sleep 60' in top['Processes'][0]

    def test_update(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sleep 60", detach=True,
                                          host_config={'CpuShares': 2})
        assert container.attrs['HostConfig']['CpuShares'] == 2
        container.update(cpu_shares=3)
        container = client.containers.get(container.id)
        assert container.attrs['HostConfig']['CpuShares'] == 3

    def test_wait(self):
        client = docker.from_env()
        container = client.containers.run("alpine", "sh -c 'exit 0'",
                                          detach=True)
        assert container.wait() == 0
        container = client.containers.run("alpine", "sh -c 'exit 1'",
                                          detach=True)
        assert container.wait() == 1
