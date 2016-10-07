==================================
Build Qemu and Libvirt from source
==================================

*Abstract:* Build and install Libvirt and Qemu from source. A version can be
specified. As the sources are from the git repos, the version can be anything
which can be checked out, for example a tag / branch / commit.

Quickstart
==========

Add the *Vagrant* box we will use for the VMs. That needs to be done only once::

    [user@host]$ vagrant box add ubuntu-trusty64 https://atlas.hashicorp.com/ubuntu/boxes/trusty64/

Start the VMs and wait until they are finished::

    [user@host]$ vagrant up

Log into the node::

    [user@host]$ vagrant ssh

Build and install newer versions of libvirt and qemu with::

    vagrant@qemu-src:~$ cd ~
    vagrant@qemu-src:~$ cp /vagrant/files/build.sh .
    vagrant@qemu-src:~$ ./build.sh --qemu-version v2.7.0 --libvirt-version v1.3.3

Switch the user which should be used to interact with *Devstack*::

    vagrant@qemu-src:~$ sudo su - stack

Apply the *Devstack* patch which prevents the reinstallation of libvirt/qemu::

    git apply /vagrant/files/devstack-libvirt-qemu.patch

Change to the *Devstack* folder and start it::

    stack@qemu-src:~$ cd /opt/stack/devstack
    stack@qemu-src:~$ make stack

Wait for *Devstack* to finish. You should see something like this::

    This is your host IP address: 192.168.67.180
    This is your host IPv6 address: ::1
    Horizon is now available at http://192.168.67.180/dashboard
    Keystone is serving at http://192.168.67.180/identity/
    The default users are: admin and demo
    The password: openstack

In case the `virtlogd` feature is not yet merged in upstream Nova code,
use the script to download the patches and apply them::

    stack@qemu-src:~$ cd /opt/stack/nova
    stack@qemu-src:~$ cp /vagrant/files/nova-virtlogd-patches.sh .
    stack@qemu-src:~$ ./nova-virtlogd-patches.sh

After applying this patch, you need to restart the `n-cpu` service::

    stack@qemu-src:~$ screen -x

.. note:: In case you get the "Cannot open your terminal" error message
          you can use `script /dev/null` and then `screen -x`.