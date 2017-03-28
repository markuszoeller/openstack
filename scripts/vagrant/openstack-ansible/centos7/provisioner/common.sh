#!/usr/bin/env bash

logger "provisioning file is executed"

echo "IP addresses: `hostname -I`"

# yum upgrade

yum install -y git
yum install -y openssh-server
yum install -y python-devel

yum install -y epel-release

yum install -y redhat-lsb

yum install -y ntp
yum install -y ntpdate
systemctl enable ntpd
systemctl start ntpd

echo "date: `date`"
