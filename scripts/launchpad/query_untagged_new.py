#!/usr/bin/env python

# Displays all Launchpad bugs for a LP project which are untagged
#
# Copyright 2016 Markus Zoeller

import argparse
import datetime

import common


parser = argparse.ArgumentParser(description="Show untagged 'New' bug reports.")
parser.add_argument('-p',
                    '--project-name',
                    required=True,
                    dest='project_name',
                    help='The LP project name.')

args = parser.parse_args()

PROJECT_NAME = args.project_name

client = common.get_project_client(PROJECT_NAME)
bug_tasks = client.searchTasks(tags=["-*"],
                                status=["New"],
                                order_by="datecreated",
                                omit_duplicates=True)

print("untagged bug reports ('%s'):" % PROJECT_NAME)
print("=================================")
today = datetime.datetime.today()
for bug_task in bug_tasks:
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_created.replace(tzinfo=None)
    print(bug_task.web_link + "  (" + str(diff.days) + " days old)")
