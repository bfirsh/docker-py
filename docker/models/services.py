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
        """The version number of this service."""
        return self.attrs.get('Version').get('Index')

    def remove(self):
        """Remove this service."""
        return self.client.api.remove_service(self.id)

    def tasks(self):
        """List the tasks in this service."""
        return self.client.api.tasks(filters={'service': self.id})

    def update(self, **kwargs):
        """Update a service's configuration."""
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
        """Get a service."""
        return self.prepare_model(self.client.api.inspect_service(service_id))

    def list(self, *args, **kwargs):
        """List services."""
        return [
            self.prepare_model(s)
            for s in self.client.api.services(*args, **kwargs)
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
