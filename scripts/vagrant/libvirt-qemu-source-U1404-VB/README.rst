==================================
Build Qemu and Libvirt from source
==================================

WIP
===

.. warning:: I still need to double-check that this at least runs without error.

.. warning:: Libvirt and qemu versions are also hardcoded right now.

.. warning:: The `*.deb` files won't be created with `checkinstall`


Quickstart
==========

Add the *Vagrant* box we will use for the VMs. That needs to be done only once::

    [user@host]$ vagrant box add ubuntu-trusty64 https://atlas.hashicorp.com/ubuntu/boxes/trusty64/

Start the VMs and wait until they are finished::

    [user@host]$ vagrant up

Log into the node::

    [user@host]$ vagrant ssh

Switch the user which should be used to interact with *Devstack*::

    vagrant@controller:~$ sudo su - stack

Change to the *Devstack* folder and start it::

    stack@controller:~$ cd /opt/stack/devstack
    stack@controller:~$ make stack

Wait for *Devstack* to finish. You should see something like this::

    This is your host IP address: 192.168.67.180
    This is your host IPv6 address: ::1
    Horizon is now available at http://192.168.67.180/dashboard
    Keystone is serving at http://192.168.67.180/identity/
    The default users are: admin and demo
    The password: openstack

