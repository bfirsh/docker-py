import re

import six

from ..errors import BuildError
from ..utils.json_stream import json_stream
from .resource import Collection, Model


class Image(Model):
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)

    @property
    def name(self):
        return self.tags[0] if self.tags else self.short_id

    @property
    def short_id(self):
        """
        Returns the "sha256:" prefix plus 10 characters of the ID
        """
        if self.id.startswith('sha256:'):
            return self.id[:17]
        return self.id[:10]

    @property
    def tags(self):
        return [
            tag for tag in self.attrs.get('RepoTags', [])
            if tag != '<none>:<none>'
        ]

    def history(self):
        return self.client.api.history(self.id)

    def push(self, *args, **kwargs):
        return self.client.api.push(self.id, *args, **kwargs)

    def tag(self, *args, **kwargs):
        self.client.api.tag(self.id, *args, **kwargs)


class ImageCollection(Collection):
    model = Image

    def build(self, *args, **kwargs):
        """
        Build an image and return it.
        """
        resp = self.client.api.build(*args, **kwargs)
        if isinstance(resp, six.string_types):
            return self.get(resp)
        events = list(json_stream(resp))
        if not events:
            return BuildError('Unknown')
        event = events[-1]
        if 'stream' in event:
            match = re.search(r'Successfully built ([0-9a-f]+)',
                              event.get('stream', ''))
            if match:
                image_id = match.group(1)
                return self.get(image_id)

        raise BuildError(event.get('error') or event)

    def get(self, name):
        """
        Returns an image with the given name.
        """
        return self.prepare_model(self.client.api.inspect_image(name))

    def list(self, name=None, all=False, filters=None):
        resp = self.client.api.images(name=name, all=all, filters=filters)
        return [self.prepare_model(r) for r in resp]

    def load(self, data):
        return self.client.api.load_image(data)

    def pull(self, name, **kwargs):
        """
        Pull an image of the given name and return it.
        """
        self.client.api.pull(name, **kwargs)
        return self.get(name)

    def remove(self, *args, **kwargs):
        """
        Remove an image.
        """
        self.client.api.remove_image(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self.client.api.search(*args, **kwargs)
