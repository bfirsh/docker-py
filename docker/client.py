from .api.client import APIClient
from .models.containers import ContainerCollection
from .models.images import ImageCollection
from .models.networks import NetworkCollection
from .models.nodes import NodeCollection
from .models.services import ServiceCollection
from .models.swarm import Swarm
from .models.volumes import VolumeCollection
from .utils import kwargs_from_env


class Client(object):
    """
    A client for communicating with a Docker server.

    Example:

        >>> import docker
        >>> client = Client(base_url='unix://var/run/docker.sock')
    """
    def __init__(self, *args, **kwargs):
        self.api = APIClient(*args, **kwargs)

    @classmethod
    def from_env(cls, **kwargs):
        """
        Return a client configured with the standard set of Docker environment
        variables. The environment variables used are:

        .. envvar:: DOCKER_HOST

            The URL to the Docker host.


        .. envvar:: DOCKER_TLS_VERIFY

            Verify the host against a CA certificate.

        .. envvar:: DOCKER_CERT_PATH

            A path to a directory containing TLS certificates to use when
            connecting to the Docker host.

        Args:
            version (str): The version of the API to use. Set to ``auto`` to
                automatically detect the server's version. Default: ``1.24``
            timeout (int): Default timeout for API calls, in seconds.
            ssl_version (int): A valid `SSL version`_.
            assert_hostname (bool): Verify the hostname of the server.
            environment (dict): The environment to read environment variables
                from. Default: the value of ``os.environ``

        Example:

            >>> import docker
            >>> client = docker.from_env()

        .. _`SSL version`:
            https://docs.python.org/3.5/library/ssl.html#ssl.PROTOCOL_TLSv1
        """
        timeout = kwargs.pop('timeout', None)
        version = kwargs.pop('version', None)
        return cls(timeout=timeout, version=version,
                   **kwargs_from_env(**kwargs))

    # Resources
    @property
    def containers(self):
        """
        An object for managing containers on the server. See the
        :doc:`containers documentation <containers>` for full details.
        """
        return ContainerCollection(client=self)

    @property
    def images(self):
        """
        An object for managing images on the server. See the
        :doc:`images documentation <images>` for full details.
        """
        return ImageCollection(client=self)

    @property
    def networks(self):
        """
        An object for managing networks on the server. See the
        :doc:`networks documentation <networks>` for full details.
        """
        return NetworkCollection(client=self)

    @property
    def nodes(self):
        """
        An object for managing nodes on the server. See the
        :doc:`nodes documentation <nodes>` for full details.
        """
        return NodeCollection(client=self)

    @property
    def services(self):
        """
        An object for managing services on the server. See the
        :doc:`services documentation <services>` for full details.
        """
        return ServiceCollection(client=self)

    @property
    def swarm(self):
        """
        An object for managing a swarm on the server. See the
        :doc:`swarm documentation <swarm>` for full details.
        """
        return Swarm(client=self)

    @property
    def volumes(self):
        """
        An object for managing volumes on the server. See the
        :doc:`volumes documentation <volumes>` for full details.
        """
        return VolumeCollection(client=self)

    # Top-level methods
    def events(self, *args, **kwargs):
        return self.api.events(*args, **kwargs)
    events.__doc__ = APIClient.events.__doc__

    def info(self, *args, **kwargs):
        return self.api.info(*args, **kwargs)
    info.__doc__ = APIClient.info.__doc__

    def login(self, *args, **kwargs):
        return self.api.login(*args, **kwargs)
    login.__doc__ = APIClient.login.__doc__

    def ping(self, *args, **kwargs):
        return self.api.ping(*args, **kwargs)
    ping.__doc__ = APIClient.ping.__doc__

    def version(self, *args, **kwargs):
        return self.api.version(*args, **kwargs)
    version.__doc__ = APIClient.version.__doc__

from_env = Client.from_env
