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
    devstack/tools/create-stack-user.sh &>/dev/null
    cp /home/vagrant/local.conf devstack/  # copy local.conf
    chown -R stack /opt/stack &>/dev/null 
    # don't execute stack yet, just prepare everything for it
fi


# ====================================
# Configure (unsecured) live migration
# ====================================
# This provisioner is used for the controller node too. That node doesn't have
# a hypervisor as it doesn't serve with compute node capability. That's why we
# ask for the existence of the libvirt directory here.
if [ -d "/etc/libvirt/" ]; then
    echo "Configuring live-migration via TCP..."
    sed -i '/^\#listen_tls/c\listen_tls = 0' /etc/libvirt/libvirtd.conf
    sed -i '/^\#listen_tcp/c\listen_tcp = 1' /etc/libvirt/libvirtd.conf
    sed -i '/^\#auth_tcp/c\auth_tcp = "none"' /etc/libvirt/libvirtd.conf
    sed -i '/^libvirtd_opts=/c\libvirtd_opts="-d -l"' /etc/default/libvirt-bin # the old (deprecated) way 
    sed -i '/^env libvirtd_opts=/c\env libvirtd_opts="-d -l"' /etc/init/libvirt-bin.conf # the new way 
    service libvirt-bin restart &>/dev/null
    echo "The live-migration via TCP is configured."
fi

# The live-migration happens with host name resolution, that's why we
# have to add them to the list of known hosts. Using a variable for the
# grep keeps the noise down.
known_hosts=`grep "192.168.56." /etc/hosts`
if [ -z "$known_hosts" ] ; then
    echo "192.168.56.150 controller" >> /etc/hosts
    echo "192.168.56.151 compute1" >> /etc/hosts
    echo "192.168.56.152 compute2" >> /etc/hosts
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
