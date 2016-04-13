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
DIST_0_6 = "0 <= m < 6"
DIST_6_12 = "6 <= m < 12"
DIST_12_18 = "12 <= m < 18"
DIST_18_24 = "18 <= m < 24"
DIST_24_N = "24 <= m"
age_dist[DIST_0_6] = copy.deepcopy(status_dist)
age_dist[DIST_6_12] = copy.deepcopy(status_dist)
age_dist[DIST_12_18] = copy.deepcopy(status_dist)
age_dist[DIST_18_24] = copy.deepcopy(status_dist)
age_dist[DIST_24_N] = copy.deepcopy(status_dist)


today = datetime.datetime.today()
for bug_task in bug_tasks:
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_created.replace(tzinfo=None)

    m = diff.days / 30
    if 0 <= m < 6:
        age_dist[DIST_0_6][bug_task.status] += 1
    elif 6 <= m < 12:
        age_dist[DIST_6_12][bug_task.status] += 1
    elif 12 <= m < 18:
        age_dist[DIST_12_18][bug_task.status] += 1
    elif 18 <= m < 24:
        age_dist[DIST_18_24][bug_task.status] += 1
    else:
        age_dist[DIST_24_N][bug_task.status] += 1

for d in age_dist:
    print("%s [sum:%d]" % (d, sum(age_dist[d].values())))
    for s in age_dist[d]:
        print("\t%s: %s" % (s, str(age_dist[d][s])))
