Swarm
=====

.. py:module:: docker.models.swarm

`Docker Engine's swarm mode <https://docs.docker.com/engine/swarm/>`_ can be managed using the Python SDK. Once you have :doc:`created a client <client>`, all the methods for managing a swarm are under ``client.swarm``.

To use any swarm methods, or to create a service, you first need to make the Engine part of a swarm. This can be done by either initializing a new swarm with :py:meth:`~Swarm.init`, or joining an existing swarm with :py:meth:`~Swarm.join`.

These methods are available on ``client.swarm``:

.. rst-class:: hide-signature
.. py:class:: Swarm

  .. automethod:: init()
  .. automethod:: join()
  .. automethod:: leave()
  .. automethod:: update()
  .. automethod:: reload()

  .. autoattribute:: attrs
  .. autoattribute:: version
