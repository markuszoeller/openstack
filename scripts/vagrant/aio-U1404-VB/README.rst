=============================================
All-in-One (aio) - Ubuntu 1404 and Virtualbox
=============================================

Quickstart
==========

Add the *Vagrant* box we will use for the VMs. That needs to be done only once::

    [user@host]$ vagrant box add ubuntu-trusty64 https://atlas.hashicorp.com/ubuntu/boxes/trusty64/

Start the VM and wait until it is finished::

    [user@host]$ vagrant up

Check the status::

    [user@host]$ vagrant status
    Current machine states:

    aio                       running (virtualbox)

Log into the controller node::

    [user@host]$ vagrant ssh aio

Switch the user which should be used to interact with *Devstack*::

    vagrant@aio:~$ sudo su - stack

Change to the *Devstack* folder and start it::

    stack@aio:~$ cd /opt/stack/devstack
    stack@aio:~$ make stack

Wait for *Devstack* to finish. You should see something like this::

    This is your host IP address: 192.168.67.160
    This is your host IPv6 address: ::1
    Horizon is now available at http://192.168.67.160/dashboard
    Keystone is serving at http://192.168.67.160/identity/
    The default users are: admin and demo
    The password: openstack
