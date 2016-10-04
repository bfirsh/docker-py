Containers
==========

.. py:module:: docker.models.containers

Containers containers containers containers.

.. code-block:: python

    >>> import docker
    >>> client = docker.from_env()
    >>> client.containers.run('alpine', 'echo hello world')
    b'hello world\n'

Methods available on ``client.containers``:

.. rst-class:: hide-signature
.. autoclass:: ContainerCollection

  .. automethod:: create(image, command, **kwargs)
  .. automethod:: get(id_or_name)
  .. automethod:: list(**kwargs)
  .. automethod:: run(image, command, **kwargs)

Container objects
-----------------

.. autoclass:: Container()
  :members:
  :undoc-members:
