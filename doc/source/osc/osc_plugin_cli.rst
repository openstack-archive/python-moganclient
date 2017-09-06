=============================================
OpenStack Client Command-Line Interface (CLI)
=============================================

.. program:: openstack baremetalcompute
.. highlight:: bash

Synopsis
========

:program:`openstack [options] baremetalcompute` <command> [command-options]

:program:`openstack help baremetalcompute` <command>


Description
===========

The OpenStack Client plugin interacts with the Bare Metal service
through the ``openstack baremetalcompute`` command line interface (CLI).

To use ``openstack`` CLI, the OpenStackClient should be installed::

    # pip install python-openstackclient

To use the CLI, you must provide your OpenStack username, password,
project, and auth endpoint. You can use configuration options
``--os-username``, ``--os-password``, ``--os-project-id``
(or ``--os-project-name``), and ``--os-auth-url``,
or set the corresponding environment variables::

    $ export OS_USERNAME=user
    $ export OS_PASSWORD=password
    $ export OS_PROJECT_NAME=project                         # or OS_PROJECT_ID
    $ export OS_PROJECT_DOMAIN_ID=default
    $ export OS_USER_DOMAIN_ID=default
    $ export OS_IDENTITY_API_VERSION=3
    $ export OS_AUTH_URL=http://auth.example.com:5000/identity

This CLI is provided by python-openstackclient and osc-lib projects:

* https://git.openstack.org/openstack/python-openstackclient
* https://git.openstack.org/openstack/osc-lib


Getting help
============

To get a list of available (sub)commands and options, run::

    $ openstack help baremetalcompute

To get usage and options of a command, run::

    $ openstack help baremetalcompute <sub-command>


Examples
========

Get information about the openstack baremetalcompute server create command::

    $ openstack help baremetalcompute server create

Get a list of baremetalcompute flavors::

    $ openstack baremetalcompute flavor list

Boot a Bare metal server::

    $ openstack baremetalcompute server create --flavor <FLAVOR> --image <IMAGE> --nic net-id=<NETWORK> test

Get a list of baremetal nodes aggregates::

    $ openstack baremetalcompute aggregate list

Command Reference
=================

List of released CLI commands available in openstack client. These commands
can be referenced by doing ``openstack help baremetalcompute``.

.. toctree::
   :glob:
   :maxdepth: 2

   v1/index
