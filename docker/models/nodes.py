from .resource import Model, Collection


class Node(Model):
    """A node."""
    id_attribute = 'ID'


class NodeCollection(Collection):
    """Nodes on the Docker server."""
    model = Node

    def get(self, node_id):
        """Get a node."""
        return self.prepare_model(self.client.api.inspect_node(node_id))

    def list(self, *args, **kwargs):
        """List nodes."""
        return [
            self.prepare_model(n)
            for n in self.client.api.nodes(*args, **kwargs)
        ]
