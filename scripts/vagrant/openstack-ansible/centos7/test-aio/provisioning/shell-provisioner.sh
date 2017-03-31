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