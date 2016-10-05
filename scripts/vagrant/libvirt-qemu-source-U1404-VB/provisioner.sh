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
apt-get -qq install -y language-pack-en-base &>/dev/null
apt-get -qq install -y language-pack-de-base &>/dev/null
export LANGUAGE="en_US.UTF-8"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
locale-gen en_US.UTF-8 &>/dev/null
dpkg-reconfigure locales &>/dev/null

# ==================
# install the basics
# ==================
apt-get update &>/dev/null
apt-get -qq install -y git &>/dev/null
apt-get -qq install -y ssh &>/dev/null
apt-get -qq install -y gcc make &>/dev/null

# ============================== 
# Install and configure devstack
# ============================== 
STACK_DIR=/opt/stack
if [ ! -d "$STACK_DIR" ]; then
    mkdir $STACK_DIR
    cd $STACK_DIR
    git clone https://git.openstack.org/openstack-dev/devstack &>/dev/null
    devstack/tools/create-stack-user.sh &>/dev/null
    cp /home/vagrant/local.conf devstack/  # Vagrantfile does the prepare step
    chown -R stack /opt/stack &>/dev/null 
    # don't execute stack yet, just prepare everything for it
fi

# ===============
# Add a swap file
# ===============
SWAPFILE_SIZE_MB=4000
has_swap=`grep "swapfile" /etc/fstab`
if [ -z "$has_swap" ]; then
    fallocate -l ${SWAPFILE_SIZE_MB}M /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap defaults 0 0' >> /etc/fstab
fi

# ==========================================
# Install newer libvirt and qemu from source
# ==========================================

# helper function to install packages without any noise
function install_silently() {
    apt-get -qq install -y $1 &>/dev/null
}

# The tooling we need to build and install qemu and libvirt
install_silently autoconf
install_silently autopoint
install_silently build-essential
install_silently checkinstall
install_silently glusterfs-server
install_silently intltool-debian
install_silently libaio-dev
install_silently libbluetooth-dev
install_silently libbrlapi-dev
install_silently libbz2-dev
install_silently libcap-dev
install_silently libcap-ng-dev
install_silently libcurl4-gnutls-dev
install_silently libcurl4-gnutls-dev
install_silently libdevmapper-dev
install_silently libfdt-dev
install_silently libglib2.0-dev
install_silently libgnutls-dev
install_silently libgoogle-perftools-dev
install_silently libgtk-3-dev
install_silently libibverbs-dev
install_silently libjpeg8-dev
install_silently liblzo2-dev
install_silently libncurses5-dev
install_silently libnl-dev
install_silently libnuma-dev
install_silently libpciaccess-dev
install_silently libpixman-1-dev
install_silently librbd-dev
install_silently librdmacm-dev
install_silently libsasl2-dev
install_silently libsdl1.2-dev
install_silently libseccomp-dev
install_silently libsnappy-dev
install_silently libssh2-1-dev
install_silently libtool
install_silently libvde-dev
install_silently libvdeplug-dev
install_silently libvte-2.90-dev
install_silently libxen-dev
install_silently libxml-parser-perl
install_silently libxml-xpath-perl
install_silently libxml2-dev
install_silently libyajl-dev
install_silently nettle-dev
install_silently pkg-config
install_silently pkg-config
install_silently python-dev
install_silently valgrind
install_silently xfslibs-dev
install_silently xsltproc
install_silently zlib1g-dev

# Build and install QEMU
mkdir ~/qemu-build
cd ~/qemu-build
git clone git://git.qemu-project.org/qemu.git
cd qemu
git checkout v2.7.0  # TODO: That's the min version I need for virtlogd
./configure --target-list=i386-linux-user,i386-softmmu,x86_64-linux-user,x86_64-softmmu \
--enable-gtk --enable-vte --enable-kvm --enable-libssh2 --enable-gnutls
make
# sudo checkinstall -D --default
sudo make install
qemu-system-x86_64 --version

# Build and install Libvirt
mkdir ~/libvirt-build
cd ~/libvirt-build
git clone git://libvirt.org/libvirt.git
cd libvirt
git checkout v1.3.3 # TODO: That's the min version I need for virtlogd
./autogen.sh --system
make
# sudo checkinstall -D --default
sudo make install
libvirtd --version