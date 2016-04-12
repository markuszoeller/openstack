#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially expired
# because they got reported for Nova versions which are not supported anymore.
#
# Copyright 2016 Markus Zoeller

import datetime
import json
import os
import requests
import sys

import common

PROJECT_NAME = "nova"
DAYS_SINCE_CREATED = 30 * 18  # 18 months
STILL_VALID_FLAG = "CONFIRMED FOR: %(release_name)s"  # UPPER CASE

client = common.get_project_client(PROJECT_NAME)
bug_tasks = client.searchTasks(status=["New", "Confirmed", "Triaged"],
                               omit_duplicates=True,
                               order_by="datecreated")

SUPPORTED_RELEASE_NAMES = []

SUPPORTED_RELEASE_NAMES.append(client.development_focus.name)  # master name
for s in client.series:
    if s.active:
        SUPPORTED_RELEASE_NAMES.append(s.name)  # stable branch names
print(SUPPORTED_RELEASE_NAMES)

print("potentially expired bugs:")
print("=========================")
today = datetime.datetime.today()
counter = 0

def bug_is_still_valid(bug):
    for message in bug.messages:
        for release_name in SUPPORTED_RELEASE_NAMES:
            flag = STILL_VALID_FLAG % {'release_name': release_name.upper()}
            if flag in message.content:
                return True
    return False

for bug_task in bug_tasks:
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_created.replace(tzinfo=None)
    if diff.days < DAYS_SINCE_CREATED:
        break

    if bug_is_still_valid(bug_task.bug):
        continue

    print("%s (%d days)" %(bug_task.web_link, diff.days))
    counter += 1

print("---------------------------------")
print("%s potentially expired bug reports" % counter)