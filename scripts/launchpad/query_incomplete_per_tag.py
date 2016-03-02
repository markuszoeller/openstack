#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# ARGS (positional): The tag names to filter by. If not provided, all tags
#                    will be included.
# Example 1: python query_incomplete_per_tag.py api libvirt
# Example 2: python query_incomplete_per_tag.py
#
# Copyright 2016 Markus Zoeller

import datetime
import json
import os
import requests
import sys

import common

PROJECT_NAME = "nova"

TAGS = None if len(sys.argv) <= 1 else sys.argv[1:]

client = common.get_project_client(PROJECT_NAME)
bug_tasks = client.searchTasks(status=["Incomplete"],
                               tags=TAGS,
                               omit_duplicates=True)

print("Incomplete bugs of tags: " + str(TAGS))
print("============================")
today = datetime.datetime.today()

for bug_task in sorted(bug_tasks, key=lambda bug_task: bug_task.date_incomplete):
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_incomplete.replace(tzinfo=None)
    print(bug_task.web_link + "  (" + str(diff.days) + " days since incomplete)")

