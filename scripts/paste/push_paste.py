#!/usr/bin/env python

# Paste stuff to paste.openstack.org.
# For example when pasting information from Devstack:
#     $ cd /opt/stack/devstack
#     $ ./tools/info.sh > info.txt
#     $ ./push_paste.py info.txt
#     $ http://paste.openstack.org/show/12345/

import sys
from xmlrpclib import ServerProxy

file_to_read = sys.argv[1]

s = ServerProxy('http://paste.openstack.org/xmlrpc/')
with open(file_to_read, 'r') as f:
    read_data = f.read()
    paste_id = s.pastes.newPaste('', read_data)
paste_url = "http://paste.openstack.org/show/" + str(paste_id)
print(paste_url)
