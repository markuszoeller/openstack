#!/usr/bin/env bash

logger "provisioning file is executed"

echo "IP addresses: `hostname -I`"

yum install -y epel-release

yum install -y redhat-lsb

yum install -y ntp
systemctl enable ntpd
systemctl start ntpd

echo "date: `date`"
