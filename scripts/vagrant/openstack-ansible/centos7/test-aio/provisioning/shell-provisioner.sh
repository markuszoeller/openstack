#!/usr/bin/env bash

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