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

  .. automethod:: run(image, command=None, **kwargs)
  .. automethod:: create(image, command=None, **kwargs)
  .. automethod:: get(id_or_name)
  .. automethod:: list(**kwargs)

Container objects
-----------------

.. autoclass:: Container()
  :members:
  :undoc-members:
