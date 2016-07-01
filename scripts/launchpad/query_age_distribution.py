#!/usr/bin/env python

# Displays the age distribution of all open Launchpad bugs for OpenStack/Nova.
#
# Copyright 2016 Markus Zoeller

import collections
import copy
import datetime

import common

PROJECT_NAME = "nova"

client = common.get_project_client(PROJECT_NAME)
bug_tasks = client.searchTasks(order_by="datecreated",
                               omit_duplicates=True)


status_dist = collections.OrderedDict()
status_dist["New"] = 0
status_dist["Incomplete"] = 0
status_dist["Confirmed"] = 0
status_dist["Triaged"] = 0
status_dist["In Progress"] = 0
status_dist["Fix Committed"] = 0

age_dist = collections.OrderedDict()

today = datetime.datetime.today()
for bug_task in bug_tasks:
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_created.replace(tzinfo=None)

    m = diff.days / 30
    if m not in age_dist:
        age_dist[m] = copy.deepcopy(status_dist)
    age_dist[m][bug_task.status] += 1

MAX_M = max(age_dist)
for m in range(0, MAX_M):
    if m not in age_dist:
        age_dist[m] = copy.deepcopy(status_dist)

for m in sorted(age_dist.keys(), reverse=True):
    print("%02d %s" % (m, "*" * sum(age_dist[m].values())))

for m in age_dist:
    print("%s [sum:%d]" % (m, sum(age_dist[m].values())))
    for s in age_dist[m]:
        print("\t%s: %s" % (s, str(age_dist[m][s])))
