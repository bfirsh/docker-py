from .client import Client, AutoVersionClient, from_env
from .version import version, version_info

__version__ = version
__title__ = 'docker-py'
__all__ = ["Client", "AutoVersionClient", "from_env", "version",
           "version_info", "__version__", "__title__"]
