#!/usr/bin/env bash

# ====================
# Extend the root disk
# ====================
if [ ! -d "/dev/sdb1" ]; then
    echo "increasing disk size..."
    #    fdisk /dev/sdb
    #    n  # new partition
    #    p  # primary
    #    :  # partition number
    #    : # first sector
    #    : # last sector
    #    t # type
    #    8e  # type Linux LVM
    #    w   #write
    echo -e "n\np\n\n\n\nt\n8e\nw" | fdisk /dev/sdb
    partprobe    # notify system about new partition table
    pvcreate /dev/sdb1    # create new physical volume
    vgextend VolGroup00 /dev/sdb1       # extend existing volume group
    lvextend -L +60G /dev/VolGroup00/LogVol00  # extend logical volume
    xfs_growfs /dev/VolGroup00/LogVol00   # grow the xfs filesystem in the logical volume
    df -h /   # has now more space
fi


# ===============
# Add a swap file
# ===============
SWAPFILE_SIZE_MB=8192
has_swap=`grep "swapfile" /etc/fstab`
if [ -z "$has_swap" ]; then
    # fallocate -l ${SWAPFILE_SIZE_MB}M /swapfile
    # http://unix.stackexchange.com/questions/294600/i-cant-enable-swap-space-on-centos-7
    sudo dd if=/dev/zero of=/swapfile count={SWAPFILE_SIZE_MB} bs=1MiB
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap defaults 0 0' >> /etc/fstab
fi


# ==================
# Upgrade the system
# ==================
yum -y upgrade

# ==================
# Install the basics
# ==================
yum install -y git
yum install -y openssh-server
yum install -y python-devel
yum install -y epel-release
yum install -y redhat-lsb
yum install -y ntp
yum install -y ntpdate
yum install -y ansible

# ========================
# Install the RDO packages
# ========================
yum install -y https://rdoproject.org/repos/openstack-ocata/rdo-release-ocata.rpm


# =================
# Use a time server
# =================
systemctl enable ntpd
systemctl start ntpd


# =========================
# Prepare openstack-ansible
# =========================
if [ ! -d "/opt/openstack-ansible" ]; then
    git clone https://git.openstack.org/openstack/openstack-ansible /opt/openstack-ansible
fi

echo "===================================================================="
echo " Everything is set up. you might want to reboot the VM"
echo " before you continue. After the reboot and login:"
echo " * become root: 'sudo -i' "
echo " * change into the directory /opt/openstack-ansible"
echo " and follow the quickstart guide at: "
echo " https://docs.openstack.org/developer/openstack-ansible/developer-docs/quickstart-aio.html"
echo "===================================================================="
# ------- you might want to reboot here before you continue ------->

# =====================
# Follow the quickstart
# =====================
# https://docs.openstack.org/developer/openstack-ansible/developer-docs/quickstart-aio.html
# basically:
#   git checkout -b stable/ocata origin/stable/ocata
#   scripts/bootstrap-ansible.sh
#   scripts/bootstrap-aio.sh
#   scripts/run-playbooks.sh
