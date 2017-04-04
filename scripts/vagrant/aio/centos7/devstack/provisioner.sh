#!/usr/bin/env bash

# *************************************************
# Goal: 
# Prepare this node to play the role of an
# OpenStack node, setup by Devstack.
# 
# Basic assumptions:
# * This is used with Vagrant and Virtualbox
# * The operating system is Centos7
# * This script mutes a lot of the output noise.
# *************************************************


# ==================================================
# configure stuff for vagrant to keep the noise down
# ==================================================
#sed -i 's/^mesg n$/tty -s \&\& mesg n/g' /root/.profile
#export DEBIAN_FRONTEND=noninteractive
#export LANGUAGE=en_US.UTF-8
#export LANG=en_US.UTF-8
#export LC_ALL=en_US.UTF-8
#locale-gen en_US.UTF-8 #&>/dev/null
#dpkg-reconfigure locales #&>/dev/null

# ==================
# install the basics
# ==================
yum upgrade #&>/dev/null
yum install -y vim #&>/dev/null
yum install -y git #&>/dev/null
yum install -y openssh-server #&>/dev/null
yum install -y python-devel #&>/dev/null
yum install -y epel-release #&>/dev/null
yum install -y ntp #&>/dev/null
yum install -y ntpdate #&>/dev/null
systemctl enable ntpd #&>/dev/null
systemctl start ntpd #&>/dev/null

# ============================== 
# Install and configure devstack
# ============================== 
STACK_DIR=/opt/stack
if [ ! -d "$STACK_DIR" ]; then
    mkdir $STACK_DIR
    cd $STACK_DIR
    git clone https://git.openstack.org/openstack-dev/devstack #&>/dev/null
    devstack/tools/create-stack-user.sh #&>/dev/null
    cp /home/vagrant/local.conf devstack/  # Vagrantfile does the prepare step
    chown -R stack /opt/stack #&>/dev/null
    # don't execute stack yet, just prepare everything for it
fi

# ===============
# Add a swap file
# ===============
SWAPFILE_SIZE_MB=8000
has_swap=`grep "swapfile" /etc/fstab`
if [ -z "$has_swap" ]; then
    # fallocate -l ${SWAPFILE_SIZE_MB}M /swapfile
    # http://unix.stackexchange.com/questions/294600/i-cant-enable-swap-space-on-centos-7
    sudo dd if=/dev/zero of=/swapfile count=${SWAPFILE_SIZE_MB} bs=1MiB
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap defaults 0 0' >> /etc/fstab
fi
