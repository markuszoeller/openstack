#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova and theirs Gerrit reviews
# for high prio bug fixes.
#
# Copyright 2015 Markus Zoeller

import os

import common

PROJECT_NAME = "nova"

client = common.get_project_client(PROJECT_NAME)

bug_tasks = client.searchTasks(tags=["*"],
                                order_by='-datecreated',
                                importance=["High", "Critical"],
                                omit_duplicates=True)

print("=================================================")
print("High|Critical Prio Bugs ")
print("=================================================")
for bug_task in bug_tasks:
    print(bug_task.web_link)

print("=================================================")
print("Reviews")
print("=================================================")
link = "https://review.openstack.org/#/q/"
link += "status:open+project:openstack/nova"
link += "+(nil"
for bug_task in bug_tasks:
    link += "+OR+message:\"#" + str(bug_task.bug.id) + "\""
link += "+),n,z"
print(link)