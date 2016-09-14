# flake8: noqa
"""
This is the docker module.
"""

from .api import APIClient
from .client import Client, from_env
from .version import version, version_info

__version__ = version
__title__ = 'docker-py'
