#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import datetime
import json
import os
import requests

import common

PROJECT_NAME = "nova"
DAYS_SINCE_IN_PROGRESS = 14

client = common.get_project_client(PROJECT_NAME)
bug_tasks = client.searchTasks(status=["In Progress"],
                                omit_duplicates=True)

print("potentially stale bugs:")
print("=======================")
today = datetime.datetime.today()

for bug_task in sorted(bug_tasks, key=lambda bug_task: bug_task.date_in_progress):
    counter_all += 1
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_in_progress.replace(tzinfo=None)
    if diff.days > DAYS_SINCE_IN_PROGRESS:
        gerrit_url="https://review.openstack.org/"
        review_url = gerrit_url + "/changes/?q=status:open+message:"+str(bug_task.bug.id)
        response = requests.get(review_url)
        reviews = json.loads(common.remove_first_line(response.text))
        if not reviews:
            counter += 1
            print(bug_task.web_link + "  (" + str(diff.days) + " days since in progress)")
