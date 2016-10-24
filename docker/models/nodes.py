from .resource import Model, Collection


class Node(Model):
    """A node in a swarm."""
    id_attribute = 'ID'


class NodeCollection(Collection):
    """Nodes on the Docker server."""
    model = Node

    def get(self, node_id):
        """
        Get a node.

        Args:
            node_id (string): ID of the node to be inspected.

        Returns:
            A :py:class:`Node` object.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.
        """
        return self.prepare_model(self.client.api.inspect_node(node_id))

    def list(self, *args, **kwargs):
        """
        List swarm nodes.

        Args:
            filters (dict): Filters to process on the nodes list. Valid
                filters: ``id``, ``name``, ``membership`` and ``role``.
                Default: ``None``

        Returns:
            A list of :py:class:`Node` objects.

        Raises:
            :py:class:`docker.errors.APIError`
                If the server returns an error.

        Example:

            >>> client.nodes.list(filters={'role': 'manager'})
        """
        return [
            self.prepare_model(n)
            for n in self.client.api.nodes(*args, **kwargs)
        ]
