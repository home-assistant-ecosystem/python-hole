python-hole
===========

Python API for interacting with a *hole instance. You know the thing that is
blocking Ads by manipulating your DNS requests and run on your single board
computer or on other hardware with different operating systems.

This module is consuming the details provided by the endpoint `/api.php` only
for now.

If you wonder why the weird name and that the usage of `*hole` instead of the
real name, please contact the trademark holder. They were unhappy with original
name of the module and came up with very funny ideas which were not feasible
or match the existing naming standards. Also, it should remind us that a
community is a vital part of every Open Source project.

This module is not supported or endorsed by that particular trademark holder.
The development happens independently, they are not providing resources and
the module may no longer work if they breaking their API endpoint.

Installation
------------

The module is available from the `Python Package Index <https://pypi.python.org/pypi>`_.

.. code:: bash

    $ pip3 install hole

Usage
-----

The file ``example.py`` contains an example about how to use this module.

Roadmap
-------

There are more features on the roadmap but there is no ETA because I prefer
to support Open Source projects were third party contributions are appreciated.

Development
-----------

For development is recommended to use a ``venv``.

.. code:: bash

    $ python3.6 -m venv .
    $ source bin/activate
    $ python3 setup.py develop

License
-------

``python-hole`` is licensed under MIT, for more details check LICENSE.
