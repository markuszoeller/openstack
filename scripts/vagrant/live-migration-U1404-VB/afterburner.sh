#!/usr/bin/env bash

echo "=== checking remote libvirt access for this multi-machine setup ..."
for node_name in "controller" "compute1" "compute2"; do
    # Check if there is remote libvirt access
    echo "=== checking access for node '$node_name' ..."
    echo "===== access: '$node_name' -> 'controller'"
    vagrant ssh ${node_name} -c 'virsh -c qemu+tcp://stack@controller/system nodeinfo'
    echo "===== access: '$node_name' -> 'compute1'"
    vagrant ssh ${node_name} -c 'virsh -c qemu+tcp://stack@compute1/system nodeinfo'
    echo "===== access: '$node_name' -> 'compute2'"
    vagrant ssh ${node_name} -c 'virsh -c qemu+tcp://stack@compute2/system nodeinfo'
    echo "=== checked access."
done
echo "=== checked remote libvirt access."
