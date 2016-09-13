from .containers import Container
from .resource import Model, Collection


class Network(Model):
    """
    A Docker network.
    """
    @property
    def name(self):
        return self.attrs['Name']

    @property
    def containers(self):
        return [
            self.client.containers.get(cid) for cid in
            self.attrs.get('Containers', {}).keys()
        ]

    def connect(self, c):
        """
        Connect a container to this network.
        """
        if isinstance(c, Container):
            c = c.id
        return self.client.api.connect_container_to_network(c, self.id)

    def disconnect(self, c):
        """
        Disconnect a container from this network.
        """
        if isinstance(c, Container):
            c = c.id
        return self.client.api.disconnect_container_from_network(c, self.id)

    def remove(self):
        """
        Remove this network.
        """
        return self.client.api.remove_network(self.id)


class NetworkCollection(Collection):
    """
    Networks on the Docker server.
    """
    model = Network

    def create(self, *args, **kwargs):
        resp = self.client.api.create_network(*args, **kwargs)
        return self.get(resp['Id'])

    def get(self, network_id):
        return self.prepare_model(self.client.api.inspect_network(network_id))

    def list(self, *args, **kwargs):
        resp = self.client.api.networks(*args, **kwargs)
        return [self.prepare_model(item) for item in resp]
