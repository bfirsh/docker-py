from docker.errors import APIError
from ..errors import ContainerError
from .images import Image
from .resource import Collection, Model


class Container(Model):

    @property
    def name(self):
        """
        Returns the name of the container.
        """
        if self.attrs.get('Name') is not None:
            return self.attrs['Name'].lstrip('/')

    @property
    def status(self):
        """
        Returns the status of the container. For example, `running`, or
        `exited`.
        """
        return self.attrs['State']['Status']

    def attach(self, *args, **kwargs):
        return self.client.api.attach(self.id, *args, **kwargs)

    def commit(self, *args, **kwargs):
        resp = self.client.api.commit(self.id, *args, **kwargs)
        return self.client.images.get(resp['Id'])

    def diff(self, *args, **kwargs):
        return self.client.api.diff(self.id, *args, **kwargs)

    def exec_run(self, cmd, stdout=True, stderr=True, stdin=False, tty=False,
                 privileged=False, user='', detach=False, stream=False,
                 socket=False):
        resp = self.client.api.exec_create(
            self.id, cmd, stdout=stdout, stderr=stderr, stdin=stdin, tty=tty,
            privileged=privileged, user=user
        )
        return self.client.api.exec_start(
            resp['Id'], detach=detach, tty=tty, stream=stream, socket=socket
        )

    def export(self, *args, **kwargs):
        return self.client.api.export(self.id, *args, **kwargs)

    def get_archive(self, *args, **kwargs):
        return self.client.api.get_archive(self.id, *args, **kwargs)

    def kill(self, *args, **kwargs):
        return self.client.api.kill(self.id, *args, **kwargs)

    def logs(self, *args, **kwargs):
        return self.client.api.logs(self.id, *args, **kwargs)

    def pause(self, *args, **kwargs):
        return self.client.api.pause(self.id, *args, **kwargs)

    def put_archive(self, *args, **kwargs):
        return self.client.api.put_archive(self.id, *args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.client.api.remove_container(self.id, *args, **kwargs)

    def rename(self, *args, **kwargs):
        return self.client.api.rename(self.id, *args, **kwargs)

    def resize(self, *args, **kwargs):
        return self.client.api.resize(self.id, *args, **kwargs)

    def restart(self, *args, **kwargs):
        return self.client.api.restart(self.id, *args, **kwargs)

    def start(self, *args, **kwargs):
        return self.client.api.start(self.id, *args, **kwargs)

    def stats(self, *args, **kwargs):
        return self.client.api.stats(self.id, *args, **kwargs)

    def stop(self, *args, **kwargs):
        return self.client.api.stop(self.id, *args, **kwargs)

    def top(self, *args, **kwargs):
        return self.client.api.top(self.id, *args, **kwargs)

    def unpause(self, *args, **kwargs):
        return self.client.api.unpause(self.id, *args, **kwargs)

    def update(self, *args, **kwargs):
        return self.client.api.update_container(self.id, *args, **kwargs)

    def wait(self, *args, **kwargs):
        return self.client.api.wait(self.id, *args, **kwargs)


class ContainerCollection(Collection):
    model = Container

    def run(self, image, command=None, stdout=True, stderr=False, **kwargs):
        if isinstance(image, Image):
            image = image.id
        detach = kwargs.get("detach", False)
        try:
            container = self.create(image, command, **kwargs)
        except APIError as e:
            if e.is_image_not_found_error():
                self.client.images.pull(image)
                container = self.create(image, command, **kwargs)
            else:
                raise

        container.start()

        if detach:
            return container

        exit_status = container.wait()
        if exit_status != 0:
            raise ContainerError(
                container,
                exit_status,
                command,
                image,
                container.logs(stdout=False, stderr=True)
            )
        return container.logs(stdout=stdout, stderr=stderr)

    def create(self, image, *args, **kwargs):
        if isinstance(image, Image):
            image = image.id
        resp = self.client.api.create_container(image, *args, **kwargs)
        return self.get(resp['Id'])

    def get(self, cid):
        return self.prepare_model(self.client.api.inspect_container(cid))

    def list(self, all=False, before=None, filters=None, limit=-1, since=None):
        resp = self.client.api.containers(all=all, before=before,
                                          filters=filters, limit=limit,
                                          since=since)
        return [self.get(r['Id']) for r in resp]
