#!/usr/bin/env python

# Displays all Launchpad bugs for a LP project which block
# the creation of the release candidate.
#
# Copyright 2015 Markus Zoeller

import argparse

import common

parser = argparse.ArgumentParser()
parser.add_argument('-p',
                    '--project-name',
                    required=True,
                    dest='project_name',
                    help='The LP project name.')
parser.add_argument('-r',
                    '--release-name',
                    required=True,
                    dest='release_name',
                    help='The name of the release.')

args = parser.parse_args()

PROJECT_NAME = args.project_name

RELEASE = args.release_name

client = common.get_project_client(PROJECT_NAME)

bug_tasks = client.searchTasks(tags=[RELEASE + "-rc-potential"],
                                order_by='-datecreated',
                                omit_duplicates=True)

print("=================================================")
print("Bugs (\"" + RELEASE + "-rc-potential\") ")
print("=================================================")
for bug_task in bug_tasks:
    print(bug_task.web_link + " (" + bug_task.bug.title + ")")

print "================================================="
print "Reviews"
print "================================================="
link = "https://review.openstack.org/#/q/"
link += "status:open+project:openstack/"
link += PROJECT_NAME
link += "+(nil"
for bug_task in bug_tasks:
    link += "+OR+message:\"#" + str(bug_task.bug.id) + "\""
link += "+),n,z"
print(link)
