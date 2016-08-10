#!/usr/bin/env python

# Displays all Launchpad bugs for a LP project which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import argparse
import datetime

import common

parser = argparse.ArgumentParser()
parser.add_argument('-p',
                    '--project-name',
                    required=True,
                    dest='project_name',
                    help='The LP project name.')
parser.add_argument('-t',
                    '--tag-names',
                    dest='tags',
                    nargs='*',
                    help='The tags to filter')

args = parser.parse_args()

PROJECT_NAME = args.project_name
TAGS = args.tags

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

