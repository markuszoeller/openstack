#!/usr/bin/env bash

cd /opt/stack/nova
git fetch https://git.openstack.org/openstack/nova refs/changes/01/275801/26 \
&& git format-patch -1 --stdout FETCH_HEAD > patch-275801-26.patch
git apply patch-275801-26.patch
cd -