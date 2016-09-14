from .resource import Model, Collection


class Volume(Model):
    """A volume."""
    id_attribute = 'Name'

    @property
    def name(self):
        """The name of the volume."""
        return self.attrs['Name']

    def remove(self):
        """Remove this volume."""
        return self.client.api.remove_volume(self.id)


class VolumeCollection(Collection):
    """Volumes on the Docker server."""
    model = Volume

    def create(self, *args, **kwargs):
        """Create a volume."""
        obj = self.client.api.create_volume(*args, **kwargs)
        return self.prepare_model(obj)

    def get(self, volume_id):
        """Get a volume."""
        return self.prepare_model(self.client.api.inspect_volume(volume_id))

    def list(self, *args, **kwargs):
        """List volumes."""
        resp = self.client.api.volumes(*args, **kwargs)
        if not resp.get('Volumes'):
            return []
        return [self.prepare_model(obj) for obj in resp['Volumes']]
