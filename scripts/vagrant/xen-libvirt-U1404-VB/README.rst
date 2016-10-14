==================================
Libvirt + Xen hypervisor
==================================

*Abstract:* Use the libvirt-xen hypervisor which is used for the XEN CI
results. By that you can run tempest tests locally against xen and don't
have to wait for CI results. This is useful in case the XEN CI gives
you a `-1` on one of your patches.

Quickstart
==========

Add the *Vagrant* box we will use for the VMs. That needs to be done only once::

    [user@host]$ vagrant box add ubuntu-trusty64 https://atlas.hashicorp.com/ubuntu/boxes/trusty64/

Start the VMs and wait until they are finished::

    [user@host]$ vagrant up

Log into the node::

    [user@host]$ vagrant ssh

Switch the user which should be used to interact with *Devstack*::

    vagrant@qemu-src:~$ sudo su - stack

Change to the *Devstack* folder and start it::

    stack@qemu-src:~$ cd /opt/stack/devstack
    stack@qemu-src:~$ make stack

Wait for *Devstack* to finish. You should see something like this::

    This is your host IP address: 192.168.67.183
    This is your host IPv6 address: ::1
    Horizon is now available at http://192.168.67.180/dashboard
    Keystone is serving at http://192.168.67.180/identity/
    The default users are: admin and demo
    The password: openstack
