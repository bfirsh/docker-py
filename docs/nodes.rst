Nodes
=====

.. py:module:: docker.models.nodes

Nodes are part of a :doc:`swarm`. Methods available on ``client.nodes``:

.. rst-class:: hide-signature
.. py:class:: NodeCollection

  .. automethod:: get(id_or_name)
  .. automethod:: list(**kwargs)

Node objects
------------

.. autoclass:: Node()

  .. autoattribute:: id
  .. autoattribute:: attrs
