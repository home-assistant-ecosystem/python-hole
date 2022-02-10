python-hole
===========

Python API for interacting with a xyz-hole instance. You know the thing that is
blocking Ads by manipulating your DNS requests and run on your single board
computer or on other hardware with different operating systems.

This module is consuming the details provided by the endpoint ``api.php`` only
for now.

If you wonder why the weird name and that the usage of xzy-hole instead of the
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

On a Fedora-based system.

.. code:: bash

    $ sudo dnf -y install python-hole

For Nix or NixOS is a `pre-packed module <https://search.nixos.org/packages?channel=unstable&from=0&size=50&sort=relevance&query=hole>`_
available. The lastest release is usually present in the ``unstable`` channel.

.. code:: bash

    $ nix-env -iA nixos.python3Packages.hole

Usage
-----

The file ``example.py`` contains an example about how to use this module.

Roadmap
-------

There are more features on the roadmap but there is no ETA because I prefer
to support Open Source projects were third party contributions are appreciated.

License
-------

``python-hole`` is licensed under MIT, for more details check LICENSE.
