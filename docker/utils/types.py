# Compatibility module. See https://github.com/docker/docker-py/issues/1196

import warnings

from ..types import Ulimit, LogConfig

__all__ = ["Ulimit", "LogConfig"]

warnings.warn('docker.utils.types is now docker.types', ImportWarning)
