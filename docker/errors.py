import requests


class DockerException(Exception):
    pass


def create_api_error_from_http_exception(e):
    """
    Create a suitable APIError from requests.exceptions.HTTPError.
    """
    response = e.response
    try:
        explanation = response.json()['message']
    except ValueError:
        explanation = response.content.strip()
    cls = APIError
    if response.status_code == 404:
        if explanation and 'No such image' in str(explanation):
            cls = ImageNotFound
        else:
            cls = NotFound
    raise cls(e, response=response, explanation=explanation)


class APIError(requests.exceptions.HTTPError, DockerException):
    def __init__(self, message, response=None, explanation=None):
        # requests 1.2 supports response as a keyword argument, but
        # requests 1.1 doesn't
        super(APIError, self).__init__(message)
        self.response = response
        self.explanation = explanation

    def __str__(self):
        message = super(APIError, self).__str__()

        if self.is_client_error():
            message = '{0} Client Error: {1}'.format(
                self.response.status_code, self.response.reason)

        elif self.is_server_error():
            message = '{0} Server Error: {1}'.format(
                self.response.status_code, self.response.reason)

        if self.explanation:
            message = '{0} ("{1}")'.format(message, self.explanation)

        return message

    @property
    def status_code(self):
        if self.response:
            return self.response.status_code

    def is_client_error(self):
        if self.status_code is None:
            return False
        return 400 <= self.status_code < 500

    def is_server_error(self):
        if self.status_code is None:
            return False
        return 500 <= self.status_code < 600


class NotFound(APIError):
    pass


class ImageNotFound(NotFound):
    pass


class InvalidVersion(DockerException):
    pass


class InvalidRepository(DockerException):
    pass


class InvalidConfigFile(DockerException):
    pass


class DeprecatedMethod(DockerException):
    pass


class TLSParameterError(DockerException):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg + (". TLS configurations should map the Docker CLI "
                           "client configurations. See "
                           "https://docs.docker.com/engine/articles/https/ "
                           "for API details.")


class NullResource(DockerException, ValueError):
    pass


class ContainerError(DockerException):
    """
    Represents a container that has exited with a non-zero exit code.
    """
    def __init__(self, container, exit_status, command, image, stderr):
        self.container = container
        self.exit_status = exit_status
        self.command = command
        self.image = image
        self.stderr = stderr
        msg = ("Command '{}' in image '{}' returned non-zero exit status {}: "
               "{}").format(command, image, exit_status, stderr)
        super(ContainerError, self).__init__(msg)


class StreamParseError(RuntimeError):
    def __init__(self, reason):
        self.msg = reason


class BuildError(Exception):
    pass


def create_unexpected_kwargs_error(name, kwargs):
    quoted_kwargs = ["'{}'".format(k) for k in sorted(kwargs)]
    text = ["{}() ".format(name)]
    if len(quoted_kwargs) == 1:
        text.append("got an unexpected keyword argument ")
    else:
        text.append("got unexpected keyword arguments ")
    text.append(', '.join(quoted_kwargs))
    return TypeError(''.join(text))
