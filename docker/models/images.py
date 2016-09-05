from .resource import Collection, Model


class Image(Model):
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name)

    @property
    def short_id(self):
        """
        Returns the "sha256:" prefix plus 10 characters of the ID
        """
        return self.id[:17]

    @property
    def name(self):
        return self.tags[0] if self.tags else self.short_id

    @property
    def tags(self):
        return [
            tag for tag in self.attrs['RepoTags']
            if tag != '<none>:<none>'
        ]

    def history(self):
        return self.client.api.history(self.id)

    def push(self):
        return self.client.api.push(self.id)

    def tag(self, *args, **kwargs):
        self.client.api.tag(self.id, *args, **kwargs)


class ImageCollection(Collection):
    model = Image

    def build(self, *args, **kwargs):
        """
        Build an image and return it.
        """
        image_id = self.client.api.build(*args, **kwargs)
        return self.get(image_id)

    def get(self, name):
        """
        Returns an image with the given name.
        """
        return self.prepare_model(self.client.api.inspect_image(name))

    def pull(self, name, **kwargs):
        """
        Pull an image of the given name and return it.
        """
        self.client.api.pull(name, **kwargs)
        return self.get(name)

    def list(self, *args, **kwargs):
        return [
            self.prepare_model(r)
            for r in self.client.api.images(*args, **kwargs)
        ]

    def remove(self, *args, **kwargs):
        """
        Remove an image.
        """
        self.client.api.remove_image(*args, **kwargs)
