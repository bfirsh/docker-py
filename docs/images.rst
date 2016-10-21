Images
======

.. py:module:: docker.models.images

Manage images on the server.

Methods available on ``client.images``:

.. rst-class:: hide-signature
.. py:class:: ImageCollection

  .. automethod:: build
  .. automethod:: get
  .. automethod:: list(**kwargs)
  .. automethod:: load
  .. automethod:: pull
  .. automethod:: remove
  .. automethod:: search


Image objects
-------------

.. autoclass:: Image()

  .. autoattribute:: id
  .. autoattribute:: short_id
  .. autoattribute:: name
  .. autoattribute:: tags
  .. py:attribute:: attrs

    The raw representation of this object from the server.


  .. automethod:: history
  .. automethod:: push
  .. automethod:: reload
  .. automethod:: tag
