#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import argparse
import datetime
import json
import requests

import common

parser = argparse.ArgumentParser()
parser.add_argument('-p',
                    '--project-name',
                    required=True,
                    dest='project_name',
                    help='The LP project name.')

args = parser.parse_args()

PROJECT_NAME = args.project_name
DAYS_SINCE_IN_PROGRESS = 14

client = common.get_project_client(PROJECT_NAME)
bug_tasks = client.searchTasks(status=["In Progress"],
                                omit_duplicates=True)

print("potentially stale bugs:")
print("=======================")
today = datetime.datetime.today()
counter = 0

for bug_task in sorted(bug_tasks, key=lambda bug_task: bug_task.date_in_progress):
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_in_progress.replace(tzinfo=None)
    if diff.days > DAYS_SINCE_IN_PROGRESS:
        gerrit_url="https://review.openstack.org/"
        review_url = gerrit_url + "/changes/?q=status:open+message:"+str(bug_task.bug.id)
        response = requests.get(review_url)
        reviews = json.loads(common.remove_first_line(response.text))
        if not reviews:
            print(bug_task.web_link + "  (" + str(diff.days) + " days since in progress)")
            counter += 1

print("---------------------------------")
print("%s potentially stale bug reports" % counter)
