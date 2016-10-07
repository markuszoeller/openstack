#!/usr/bin/env bash

# ===========================================================================
# Build libvirt and qemu for git repos for a specific commit/tag/branch
#
# Examples:
# ./build.sh --libvirt-version v1.3.3  --qemu-version v2.7.0
# ./build.sh -l v1.3.3  -q v2.7.0
# ./build.sh  # uses latest greatest for libvirt and qemu
# ===========================================================================


# === RESOURCES =============================================================
# http://lost-and-found-narihiro.blogspot.co.uk/2012/02/linux-mint-12-build-qemu-kvm-libvirt.html
# http://packaging.ubuntu.com/de/html/packaging-new-software.html
# http://wiki.libvirt.org/page/Determining_version_information,_dealing_with_%22unknown_procedure%22
# http://askubuntu.com/a/695903
# https://linuxconfig.org/easy-way-to-create-a-debian-package-and-local-package-repository
# http://www.atrixnet.com/compile-qemu-from-source-and-make-a-debian-package-with-checkinstall/


# === Variables =============================================================
STACK_USER="stack"
LIBVIRT_VERSION="master"
QEMU_VERSION="master"


# === Script arguments ======================================================
while [[ $# -gt 1 ]]
do
key="$1"
case ${key} in
    -l|--libvirt-version)
    LIBVIRT_VERSION="$2"
    shift
    ;;
    -q|--qemu-version)
    QEMU_VERSION="$2"
    shift
    ;;
    *)
    echo "Option $2 is not known and is ignored."
    ;;
esac
shift # past argument or value
done


# === functions =============================================================
# helper function to install packages without any noise
function install_package() {
    sudo apt-get -qq install -y $1 > /dev/null
}

function log() {
    echo "=== LOG ===: $1"
}


# === Start the build process ===============================================
log "Building and installing libvirt '${LIBVIRT_VERSION}' and QEMU '${QEMU_VERSION}'..."


# === building and installing QEMU ==========================================
log "creating the folders for the qemu build..."
mkdir -p ~/qemu-build
cd ~/qemu-build
log "installing the packages to build Qemu..."
sudo apt-get build-dep qemu -y
install_package libgtk-3-dev
install_package libvte-2.90-dev
install_package libssh2-1-dev
if [ ! -d "qemu" ]; then
    log "Downloading the qemu repo..."
    git clone git://git.qemu-project.org/qemu.git
    cd qemu
else
    cd qemu
    log "Updating the already downloaded qemu repo..."
    git pull
fi
log "Checking out the demanded version ${QEMU_VERSION} of Qemu..."
git checkout "${QEMU_VERSION}"
log "Starting the configuration, building and installation of Qemu, this takes a while, grab a cup of coffee..."
./configure --target-list=i386-linux-user,i386-softmmu,x86_64-linux-user,x86_64-softmmu \
--enable-gtk --enable-vte --enable-kvm --enable-libssh2 --enable-gnutls && \
make -j"$(nproc)" && sudo make install
log "Installed Qemu in version: `sudo qemu-system-x86_64 --version`."


# === building and installing Libvirt =======================================
log "creating the folders for the libvirt build..."
mkdir -p ~/libvirt-build
cd ~/libvirt-build
log "installing the packages to build libvirt..."
sudo apt-get build-dep libvirt -y
install_package python-guestfs
install_package xsltproc
install_package libxml-xpath-perl
if [ ! -d "libvirt" ]; then
    log "Downloading the libvirt repo..."
    git clone git://libvirt.org/libvirt.git
    cd libvirt
else
    cd libvirt
    log "Updating the already downloaded libvirt repo..."
    git pull
fi
log "Checking out the demanded version ${LIBVIRT_VERSION} of libvirt..."
git checkout "${LIBVIRT_VERSION}"
log "Starting the configuration, building and installation of Libvirt, this takes a while, grab a biscuit..."
./autogen.sh --system && make -j"$(nproc)" && sudo make install
log "Installed Libvirt in version: `sudo libvirtd --version`."

# === Configure the Policy Kit for libvirt ==================================
# Polkit configurations as "stack" user!!
log "Configuring the policy kit for libvirt..."
cat <<EOF | sudo tee /etc/polkit-1/localauthority/50-local.d/50-libvirt-remote-access.pkla
[libvirt Management Access]
Identity=unix-user:${STACK_USER}
Action=org.libvirt.unix.manage
ResultAny=yes
ResultInactive=yes
ResultActive=yes
EOF

# === Start the libvirt daemon(s) ===========================================
log "If libvirtd is already running, we kill it (and start it later)..."
sudo pkill -f "libvirtd" || true
log "Starting the libvirt daemon..."
sudo libvirtd --verbose --daemon

# NOTE: Since libvirt 1.3.0 "virtlogd" is a mandatory service:
# https://bugzilla.redhat.com/show_bug.cgi?id=1290357
log "If virtlogd is already running, we kill it (and start it later)..."
sudo pkill -f "virtlogd" || true
log "Trying to start virtlogd as daemon process..."
sudo virtlogd --verbose --daemon || true


# === check the installation ================================================
log "Everything is set up, the stack user should be able to connect to the hypervisor..."
sudo su -c "virsh -c qemu:///system version" ${STACK_USER}
# The output should look similar to this:
#    Compiled against library: libvirt 1.3.3
#    Using library: libvirt 1.3.3
#    Using API: QEMU 1.3.3
#    Running hypervisor: QEMU 2.7.0
