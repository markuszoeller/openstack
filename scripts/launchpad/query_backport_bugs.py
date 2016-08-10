#!/usr/bin/env python

# Queries Launchpad Bugs to see if they fit in the time frame of stable
# releases and are potential candidates for backports.
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

args = parser.parse_args()

PROJECT_NAME = args.project_name

client = common.get_project_client(PROJECT_NAME)


LP_OPEN_STATES = ["New", "Incomplete", "Confirmed", "Triaged", "In Progress"]

# The dates when the master got opened for each cycle. I used the tags
# of the previous release to determine the dates. As an example:
# The Kilo release was marked with tag '2015.1.0' which marks the point in
# time when master was open for the Liberty cycle. 
OPEN_CYCLE_DATES = {
    'kilo': datetime.datetime(2014, 10, 16),   # tag:2014.2 released Juno
    'liberty': datetime.datetime(2015, 4, 30), # tag:2015.1.0 released Kilo
    'mitaka': datetime.datetime(2015, 10, 15), # tag:12.0.0 released Liberty
#    'newton': datetime.datetime(2016, 04, ??), # tag:13.0.0 released Mitaka
#    'ocata': datetime.datetime(2016, 10, ??), # tag:14.0.0 released Newton
}

OPEN_BUG_TASKS = client.searchTasks(status=LP_OPEN_STATES,
                                    order_by='datecreated',
                                    omit_duplicates=True)


def get_backport_potentials(release_name, bug_tasks):
    backport_potentials = []
    for bug_task in bug_tasks:
        create_date = bug_task.date_created.replace(tzinfo=None)
        if create_date > OPEN_CYCLE_DATES[release_name]:
            backport_potentials.append(bug_task)
    return backport_potentials


def print_bug_details(bug_task):
    link = bug_task.web_link.encode('ascii', 'ignore').strip()
    title = bug_task.bug.title.encode('ascii', 'ignore').strip()
    print("%s (%s)" % (link, title))


def print_backport_potential(release_name, bug_tasks):
    print("=================================================")
    print("Bugs (\"" + release_name + "-backport-potential\") ")
    print("=================================================")
    for bug_task in bug_tasks:
        print_bug_details(bug_task)


def print_backport_tags_per_bug_task(bug_tasks):
    print("=================================================")
    print("Bugs (potential backports to releases)")
    print("=================================================")
    for bug_task in bug_tasks:
        create_date = bug_task.date_created.replace(tzinfo=None)
        backports = []
        for release_name in OPEN_CYCLE_DATES:
            if create_date > OPEN_CYCLE_DATES[release_name]:
                backports.append("%s-backport-potential" % release_name)
        if backports:
            print_bug_details(bug_task)
            print("   " + ", ".join(backports))


print_backport_tags_per_bug_task(OPEN_BUG_TASKS)
print("")
for release_name in OPEN_CYCLE_DATES:
    bug_tasks = get_backport_potentials(release_name, OPEN_BUG_TASKS)
    print_backport_potential(release_name, bug_tasks)
    print("")
