
class Model(object):

    def __init__(self, attrs=None, url=None, client=None, collection=None):
        self.url = url
        self.client = client
        self.collection = collection
        self.attrs = attrs
        if self.attrs is None:
            self.attrs = {}

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.short_id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    @property
    def id(self):
        return self.attrs.get("Id")

    @property
    def short_id(self):
        return self.id[:10]

    def reload(self):
        """
        Loads this object from the server again and update `attrs` with the
        new data.
        """
        new_model = self.collection.get(self.id)
        self.attrs = new_model.attrs


class Collection(object):
    model = None

    def __init__(self, client=None, url=None):
        self.client = client
        self.url = url

    def list(self):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def create(self, attrs=None):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError

    def prepare_model(self, attrs):
        if isinstance(attrs, Model):
            attrs.client = self.client
            attrs.collection = self
            return attrs
        elif isinstance(attrs, dict):
            return self.model(attrs=attrs, client=self.client, collection=self)
        else:
            raise Exception("Can't create %s from %s" %
                            (self.model.__name__, attrs))
