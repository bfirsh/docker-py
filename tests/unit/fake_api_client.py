import docker

from . import fake_api

try:
    from unittest import mock
except ImportError:
    import mock


def make_fake_api_client():
    """
    Returns non-complete fake APIClient.

    This returns most of the default cases correctly, but most arguments that
    change behaviour will not work.
    """
    return mock.MagicMock(**{
        'build.return_value': fake_api.FAKE_IMAGE_ID,
        'commit.return_value': fake_api.post_fake_commit()[1],
        'containers.return_value': fake_api.get_fake_containers()[1],
        'create_container.return_value':
            fake_api.post_fake_create_container()[1],
        'exec_create.return_value': fake_api.post_fake_exec_create()[1],
        'exec_start.return_value': fake_api.post_fake_exec_start()[1],
        'images.return_value': fake_api.get_fake_images()[1],
        'inspect_container.return_value':
            fake_api.get_fake_inspect_container()[1],
        'inspect_image.return_value': fake_api.get_fake_inspect_image()[1],
        'logs.return_value': 'hello world\n',
        'start.return_value': None,
        'wait.return_value': 0,
    })


def make_fake_client():
    """
    Returns a Client with a fake APIClient.
    """
    client = docker.Client()
    client.api = make_fake_api_client()
    return client
