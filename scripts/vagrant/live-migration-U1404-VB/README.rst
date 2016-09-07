==============================================
Live migration with Ubuntu 1404 and Virtualbox
==============================================

Quickstart
==========

Add the *Vagrant* box we will use for the VMs. That needs to be done only once::

    [user@host]$ vagrant box add ubuntu-trusty64 https://atlas.hashicorp.com/ubuntu/boxes/trusty64/

Start the VMs and wait until they are finished::

    [user@host]$ vagrant up

Check their status::

    [user@host]$ vagrant status
    Current machine states:

    controller                running (virtualbox)
    compute1                  running (virtualbox)
    compute2                  running (virtualbox)

Log into the controller node::

    [user@host]$ vagrant ssh controller

Switch the user which should be used to interact with *Devstack*::

    vagrant@controller:~$ sudo su - stack

Change to the *Devstack* folder and start it::

    stack@controller:~$ cd /opt/stack/devstack
    stack@controller:~$ make stack

Wait for *Devstack* to finish. You should see something like this::

    This is your host IP address: 192.168.56.150
    This is your host IPv6 address: ::1
    Horizon is now available at http://192.168.56.150/dashboard
    Keystone is serving at http://192.168.56.150/identity/
    The default users are: admin and demo
    The password: openstack

Log into the compute nodes as well and start *Devstack* like above.
At the end you will see all services registered in the Horizon dashboard
at http://192.168.56.150/dashboard/admin/info/?tab=system_info__nova_services