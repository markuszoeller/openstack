#!/usr/bin/env python

# Counts all config options within the Nova source tree and displays them
# as a hierarchical tree. Copy the file to the Nova root folder and 
# execute it. 
# Example output:
#
#      nova [87]
#     --- CA [0]
#     ------ newcerts [0]
#     ------ private [0]
#     ------ projects [0]
#     ------ reqs [0]
#     --- api [3]
#     ------ ec2 [14]
#     ------ metadata [6]
#     ------ openstack [6]
#     <snip>
#
# Copyright 2016 Markus Zoeller


import os
import re
import sys

IGNORE_EMPTY_DIRS = True
ALL_OPTS_COUNTER = 0
OPTS_REGEX = r".*cfg\.[a-zA-Z]*Opt\("
PATHS_TO_IGNORE = ["locale", "tests", "__pycache__"]

if len(sys.argv) > 1 and sys.argv[1] == "--show-empty":
    IGNORE_EMPTY_DIRS = False

# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk("nova"):
    dirs.sort()
    path = root.split('/')
    name = os.path.basename(root)
    if any(x in PATHS_TO_IGNORE for x in path):
        continue

    count_opts = 0

    for f in files:
        if f.endswith(".pyc"):
            continue
        file_path = os.path.join(root, f)
        with open(file_path, 'r') as content_file:
            content = content_file.read()
            matches = re.findall(OPTS_REGEX, content)
            count_opts += len(matches)

    if IGNORE_EMPTY_DIRS and count_opts <= 0:
        continue

    print (len(path) - 1) * '---', name, "[" + str(count_opts) + "]"
    ALL_OPTS_COUNTER += count_opts

print("----------------------------")
print("Number of total options: " + str(ALL_OPTS_COUNTER))