from .unixconn import UnixAdapter

__all__ = ["UnixAdapter"]

try:
    from .npipeconn import NpipeAdapter
except ImportError:
    pass
else:
    __all__ += ["NpipeAdapter"]
