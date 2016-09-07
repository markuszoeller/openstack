======
README
======

Must do configs for each environment
====================================

In case you want to start multiple environments at once, it's good to set
some settings right from the start to different value. Below is a list to
check.

#. The SSH port forwarding (default `22 => 2222`). In `Vagrantfile` set
   this::

       config.vm.network :forwarded_port, guest: 22, host: $todo_port

#. The private network of the environment. In `Vagrantfile` set this::

       config.vm.network :private_network, ip: $todo_ip_address

