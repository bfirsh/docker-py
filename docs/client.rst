Client reference
================

.. py:module:: docker.client

Creating a client
-----------------

To communicate with the Docker daemon, you first need to instantiate a client. The easiest way to do that, is to by using the :py:func:`~docker.client.from_env`, but it can be configured manually by instantiating a :py:class:`~docker.client.Client` class directly.

.. autofunction:: from_env()

Reference
---------

.. autoclass:: Client()

  .. autoattribute:: containers
  .. autoattribute:: images
  .. autoattribute:: networks
  .. autoattribute:: nodes
  .. autoattribute:: services
  .. autoattribute:: swarm
  .. autoattribute:: volumes

  .. automethod:: events()
  .. automethod:: info()
  .. automethod:: login()
  .. automethod:: ping()
  .. automethod:: version()
