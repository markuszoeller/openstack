==============================================
Live migration with Ubuntu 1404 and Virtualbox
==============================================

Quickstart::

    [user@host]$ cd vagrant/live-migration-U1404-VB  # this folder here
    [user@host]$ # Adding the box needs to be done only once
    [user@host]$ vagrant box add ubuntu-trusty https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-i386-vagrant-disk1.box
    [user@host]$ vagrant up        # start the VMs and wait until finished
    [user@host]$ vagrant status    # check that all are ready
    Current machine states:

    controller                running (virtualbox)
    compute1                  running (virtualbox)
    compute2                  running (virtualbox)
    [user@host]$ vagrant ssh controller      # log into the controller node
    vagrant@controller:~$ sudo su - stack    # The "stack" user should use Devstack
    stack@controller:~$ cd /opt/stack/devstack
    stack@controller:~$ make stack           # Trigger Devstack installation
    stack@controller:~$ # devstack magic starts here, wait for:
    This is your host IP address: 192.168.56.150
    This is your host IPv6 address: ::1
    Horizon is now available at http://192.168.56.150/dashboard
    Keystone is serving at http://192.168.56.150/identity/
    The default users are: admin and demo
    The password: openstack

Log into the compute nodes as well and trigger Devstack like above.
At the end you will see all services registered in the Horizon dashboard
at http://192.168.56.150/dashboard
