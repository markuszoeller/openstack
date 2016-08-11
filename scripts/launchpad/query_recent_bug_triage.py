#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which block
# the creation of the release candidate.
#
# Copyright 2016 Markus Zoeller

import argparse
import os
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

RECENT_ACTIVITY_IN_DAYS = 14

start = datetime.datetime.now()

project = common.get_project_client(PROJECT_NAME)

ALL_STATES = ["New", "Incomplete", "Confirmed", "Won't Fix", "Opinion",
              "Invalid", "Fix Released"]
bug_tasks = project.searchTasks(status=ALL_STATES,
                                order_by='-date_last_updated',
                                omit_duplicates=True)

# bug_task
# https://api.launchpad.net/1.0/bugs/1533876

# bug_task.bug
# https://api.launchpad.net/1.0/nova/+bug/1533876

# bug_task.bug.related_tasks
# https://api.launchpad.net/1.0/nova/+bug/1533876/related_tasks

class StatSummary(object):
    
    def __init__(self, person_url, person_name):
        self.person_url = person_url.encode('ascii', 'replace')
        self.person_name = person_name.encode('ascii', 'replace')
        self.created_reports = []
        self.confirmed_reports = []
        self.rejected_reports = []
        self.resolved_reports = []
        self.inquired_reports = []

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
               self.person_url == other.person_url)

    def __cmp__(self,other):
        return cmp(self.person_name, other.person_name)

    def __repr__(self):
        return "<StatSummary: person=%s, created=%d, confirmed=%d, rejected=%d, resolved=%d, inquired=%d, sum=%d>" % \
            (self.person_name, self.created, self.confirmed, self.rejected, self.resolved, self.inquired, self.sum)

    @property
    def created(self):
        return len(self.created_reports)

    @property
    def confirmed(self):
        return len(self.confirmed_reports)

    @property
    def rejected(self):
        return len(self.rejected_reports)

    @property
    def resolved(self):
        return len(self.resolved_reports)

    @property
    def inquired(self):
        return len(self.inquired_reports)

    @property
    def sum(self):
        return self.created + self.confirmed + self.rejected + \
            self.resolved + self.inquired

print "================================================="
print " recent bug actions"
print "================================================="
today = datetime.datetime.today()
counter = 0
stats = {}


def get_summary(person):
    link = "unknown"
    name = "unknown"
    if person:
        link = person.web_link
        name = person.display_name
    if not link in stats.keys():
        stats[link] = StatSummary(link, name)
    return stats[link]

def is_created(bug_task, a):
    return (a.whatchanged =="bug" and a.message == "added bug" and \
            bug_task.date_created == bug_task.bug.date_created) or \
            a.whatchanged == "bug task added" and a.newvalue == PROJECT_NAME


def is_rejected(a):
    return a.newvalue in ["Invalid", "Opinion", "Won't Fix"]


def is_new_confirmed(a):
    return a.newvalue == 'Confirmed' and a.oldvalue == "New"


def is_trackable_status_change(a):
    return a.whatchanged == PROJECT_NAME + ": status" and \
           a.newvalue in ["Incomplete", "Confirmed", "Won't Fix", "Opinion",
                          "Invalid", "Fix Released"]


for bug_task in bug_tasks:
    diff = today - bug_task.bug.date_last_updated.replace(tzinfo=None)
    if diff.days > RECENT_ACTIVITY_IN_DAYS:
        break

    print("%d - %d days" % (counter, diff.days))
    for a in bug_task.bug.activity:
        diff = today - a.datechanged.replace(tzinfo=None)
        if diff.days > RECENT_ACTIVITY_IN_DAYS:
            # ignore activities which are not recent
            continue

        person = a.person

        if is_created(bug_task, a):
            get_summary(person).created_reports.append(bug_task.web_link)
        elif is_trackable_status_change(a):
            if is_rejected(a):
                get_summary(person).rejected_reports.append(bug_task.web_link)
            elif is_new_confirmed(a):
                get_summary(person).confirmed_reports.append(bug_task.web_link)
            elif a.newvalue == 'Fix Released':
                if person.web_link.encode('ascii', 'replace') == "https://launchpad.net/~hudson-openstack":
                    person = bug_task.assignee if bug_task.assignee else person
                get_summary(person).resolved_reports.append(bug_task.web_link)
            elif a.newvalue == "Incomplete":
                get_summary(person).inquired_reports.append(bug_task.web_link)
            # 
    counter += 1

print(counter)

for s in sorted(stats.values()):
    print(str(s))


end = datetime.datetime.now()
print("Duration: %s" % (end - start).seconds)
