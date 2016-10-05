#!/usr/bin/env bash

export OS_AUTH_URL=http://192.168.67.180:5000/v2.0
export OS_TENANT_NAME="demo"

# unsetting v3 items in case set
unset OS_PROJECT_ID
unset OS_PROJECT_NAME
unset OS_USER_DOMAIN_NAME

export OS_USERNAME="admin"
export OS_PASSWORD="openstack"

# If your configuration has multiple regions, we set that information here.
# OS_REGION_NAME is optional and only valid in certain environments.
export OS_REGION_NAME="RegionOne"
# Don't leave a blank variable, unset it if it was empty
if [ -z "$OS_REGION_NAME" ]; then unset OS_REGION_NAME; fi

export OS_ENDPOINT_TYPE=publicURL
export OS_INTERFACE=public
export OS_IDENTITY_API_VERSION=2
