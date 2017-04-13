#!/usr/bin/env bash

# *************************************************
# Goal: 
# Prepare this node to play the role of an
# OpenStack node, setup by Devstack.
# 
# Basic assumptions:
# * This is used with Vagrant and Virtualbox
# * The operating system is Ubuntu 14.04
# * This script mutes a lot of the output noise.
# *************************************************


# ==================================================
# configure stuff for vagrant to keep the noise down
# ==================================================
sed -i 's/^mesg n$/tty -s \&\& mesg n/g' /root/.profile
export DEBIAN_FRONTEND=noninteractive
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale-gen en_US.UTF-8 &>/dev/null
dpkg-reconfigure locales &>/dev/null

# ==================
# install the basics
# ==================
apt-get update &>/dev/null
apt-get -qq install -y git &>/dev/null
apt-get -qq install -y ssh &>/dev/null

# ============================== 
# Install and configure devstack
# ============================== 
STACK_DIR=/opt/stack
if [ ! -d "$STACK_DIR" ]; then
    mkdir $STACK_DIR
    cd $STACK_DIR
    git clone https://git.openstack.org/openstack-dev/devstack &>/dev/null
    touch /etc/motd
    echo "======================================================" >> /etc/motd
    echo " This is stable/ocata. The last release which works" >> /etc/motd
    echo " with Ubuntu 14.04. The Pike dev cycle needs Ubuntu " >> /etc/motd
    echo " 16.04 and greater. This is due to the hypervisor " >> /etc/motd
    echo " versions of libvirt/qemu. This is since this commit: " >> /etc/motd
    echo " https://github.com/openstack-dev/devstack/commit/ff10ac3" >> /etc/motd
    echo "======================================================" >> /etc/motd
    git checkout origin/stable/ocata
    devstack/tools/create-stack-user.sh &>/dev/null
    cp /home/vagrant/local.conf devstack/  # Vagrantfile does the prepare step
    chown -R stack /opt/stack &>/dev/null 
    # don't execute stack yet, just prepare everything for it
fi

# ===============
# Add a swap file
# ===============
SWAPFILE_SIZE_MB=8000
has_swap=`grep "swapfile" /etc/fstab`
if [ -z "$has_swap" ]; then
    fallocate -l ${SWAPFILE_SIZE_MB}M /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap defaults 0 0' >> /etc/fstab
fi