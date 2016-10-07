#!/usr/bin/env bash

git fetch https://git.openstack.org/openstack/nova refs/changes/80/334480/16 \
&& git format-patch -1 --stdout FETCH_HEAD > virtlogd-1_change-334480_ps-16_remove-py26-code.patch

git fetch https://git.openstack.org/openstack/nova refs/changes/65/323765/24 \
&& git format-patch -1 --stdout FETCH_HEAD > virtlogd-2_change-323765_ps-24_use-virtlogd.patch

# NOTE: as stack user (to avoid permission issues)
git apply virtlogd-1_change-334480_ps-16_remove-py26-code.patch
git apply virtlogd-2_change-323765_ps-24_use-virtlogd.patch
