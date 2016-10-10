#!/usr/bin/env bash

cd /opt/stack/tempest
git fetch https://git.openstack.org/openstack/tempest refs/changes/15/346815/13 \
&& git format-patch -1 --stdout FETCH_HEAD > patch-346815-13.patch
git apply patch-346815-13.patch
cd -