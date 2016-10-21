import inspect
from docker.types import TaskTemplate, ContainerSpec
from .resource import Model, Collection


class Service(Model):
    """A service."""
    id_attribute = 'ID'

    @property
    def name(self):
        """The service's name."""
        return self.attrs['Spec']['Name']

    @property
    def version(self):
        """
        The version number of the service. If this is not the same as the
        server, the :py:meth:`update` function will not work and you will
        need to call :py:meth:`reload` before calling it again.
        """
        return self.attrs.get('Version').get('Index')

    def remove(self):
        """
        Stop and remove the service.
        """
        return self.client.api.remove_service(self.id)

    def tasks(self, filters=None):
        """
        List the tasks in this service.

        Args:
            filters (dict): A map of filters to process on the tasks list.
                Valid filters: ``id``, ``name``, ``node``,
                ``label``, and ``desired-state``.

        Returns:
            (list): List of task dictionaries.
        """
        if filters is None:
            filters = {}
        filters['service'] = self.id
        return self.client.api.tasks(filters=filters)

    def update(self, **kwargs):
        """
        Update a service's configuration.
        """
        create_kwargs, spec_kwargs = _get_create_and_spec_kwargs(kwargs)
        # Image is required, so if it hasn't been set, use current image
        if 'image' not in spec_kwargs:
            spec = self.attrs['Spec']['TaskTemplate']['ContainerSpec']
            spec_kwargs['image'] = spec['Image']
        return self.client.api.update_service(
            self.id,
            self.version,
            TaskTemplate(ContainerSpec(**spec_kwargs)),
            **create_kwargs
        )


class ServiceCollection(Collection):
    """Services on the Docker server."""
    model = Service

    def create(self, **kwargs):
        """Create a service."""
        create_kwargs, spec_kwargs = _get_create_and_spec_kwargs(kwargs)
        service_id = self.client.api.create_service(
            TaskTemplate(ContainerSpec(**spec_kwargs)),
            **create_kwargs
        )
        return self.get(service_id)

    def get(self, service_id):
        """
        Get a service.

        Args:
            service_id (str): The ID of the service.

        Returns:
            (:py:class:`Service`): The service.

        Raises:
            :py:class:`docker.errors.NotFound` If the service does not exist.
        """
        return self.prepare_model(self.client.api.inspect_service(service_id))

    def list(self, **kwargs):
        """
        List services.

        Args:
            filters (dict): Filters to process on the nodes list. Valid
                filters: ``id`` and ``name``. Default: ``None``.

        Returns:
            (list of :py:class:`Service`): The services.
        """
        return [
            self.prepare_model(s)
            for s in self.client.api.services(**kwargs)
        ]


def _container_spec_kwargs():
    if hasattr(inspect, 'signature'):
        args = inspect.signature(ContainerSpec.__init__).parameters.keys()
    else:
        args = inspect.getargspec(ContainerSpec.__init__).args
    return [a for a in args if a != 'self']


def _get_create_and_spec_kwargs(kwargs):
    # TODO: raise exception for unknown kwargs
    create_kwargs = {}
    spec_kwargs = {}
    for key, value in kwargs.items():
        if key == 'labels':
            create_kwargs['labels'] = value
        elif key == 'container_labels':
            spec_kwargs['labels'] = value
        elif key in _container_spec_kwargs():
            spec_kwargs[key] = value
        else:
            create_kwargs[key] = value
    return create_kwargs, spec_kwargs
