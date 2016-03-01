#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which block
# the creation of the release candidate.
#
# Copyright 2015 Markus Zoeller

import os

import common

PROJECT_NAME = "nova"

RELEASE="mitaka"

client = common.get_project_client(PROJECT_NAME)

bug_tasks = client.searchTasks(tags=[RELEASE + "-rc-potential"],
                                order_by='-datecreated',
                                omit_duplicates=True)

print("=================================================")
print("Bugs (\"" + RELEASE + "-rc-potential\") ")
print("=================================================")
for bug_task in bug_tasks:
    print(bug_task.web_link)

print "================================================="
print "Reviews"
print "================================================="
link = "https://review.openstack.org/#/q/"
link += "status:open+project:openstack/nova"
link += "+(nil"
for bug_task in bug_tasks:
    link += "+OR+message:\"#" + str(bug_task.bug.id) + "\""
link += "+),n,z"
print(link)
