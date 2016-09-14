from docker.errors import APIError
from docker.types import SwarmSpec
from .resource import Model


class Swarm(Model):
    """
    The server's Swarm state. This a singleton that must be reloaded to get
    the current state of the Swarm.
    """

    def __init__(self, *args, **kwargs):
        super(Swarm, self).__init__(*args, **kwargs)
        if self.client:
            try:
                self.reload()
            except APIError as e:
                if e.response.status_code != 406:
                    raise

    @property
    def version(self):
        """
        The version number of this Swarm.
        """
        return self.attrs.get('Version').get('Index')

    def init(self, advertise_addr=None, listen_addr='0.0.0.0:2377',
             force_new_cluster=False, swarm_spec=None, **kwargs):
        """
        Initialize the Swarm.
        """
        init_kwargs = {}
        for arg in ['advertise_addr', 'listen_addr', 'force_new_cluster']:
            if arg in kwargs:
                init_kwargs[arg] = kwargs[arg]
                del kwargs[arg]
        init_kwargs['swarm_spec'] = SwarmSpec(**kwargs)
        self.client.api.init_swarm(**init_kwargs)
        self.reload()

    def leave(self, *args, **kwargs):
        """
        Leave the Swarm.
        """
        return self.client.api.leave_swarm(*args, **kwargs)

    def reload(self):
        """
        Load the Swarm from the server.
        """
        self.attrs = self.client.api.inspect_swarm()

    def update(self, rotate_worker_token=False, rotate_manager_token=False,
               **kwargs):
        """
        Update the Swarm's configuration.
        """
        # TODO: this seems to have to be set?
        if kwargs.get('node_cert_expiry') is None:
            kwargs['node_cert_expiry'] = 7776000000000000

        return self.client.api.update_swarm(
            version=self.version,
            swarm_spec=SwarmSpec(**kwargs),
            rotate_worker_token=rotate_worker_token,
            rotate_manager_token=rotate_manager_token
        )
