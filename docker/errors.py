import requests


class APIError(requests.exceptions.HTTPError):
    def __init__(self, message, response, explanation=None):
        # requests 1.2 supports response as a keyword argument, but
        # requests 1.1 doesn't
        super(APIError, self).__init__(message)
        self.response = response

        self.explanation = explanation

        if self.explanation is None and response.content:
            try:
                self.explanation = response.json()['message']
            except ValueError:
                self.explanation = response.content.strip()

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

    def is_client_error(self):
        return 400 <= self.response.status_code < 500

    def is_server_error(self):
        return 500 <= self.response.status_code < 600

    def is_image_not_found_error(self):
        """
        Returns whether this error is an image not found error.
        """
        return (self.response.status_code == 404 and
                self.explanation and
                'No such image' in str(self.explanation))


class DockerException(Exception):
    pass


class NotFound(APIError):
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


class ContainerError(Exception):
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
