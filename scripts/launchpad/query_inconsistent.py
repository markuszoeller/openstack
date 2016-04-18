#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import datetime
import json
import os
import requests
import logging

import common

PROJECT_NAME = "nova"
LOG = logging.getLogger(__name__)

client = common.get_project_client(PROJECT_NAME)

def get_inconsistent_reports():
    LOG.info("getting inconsistent reports...")
    inconsistent = []
    today = datetime.datetime.today()
    lp_project = common.get_project_client(PROJECT_NAME)

    bug_tasks = lp_project.searchTasks(status=["In Progress"],
                                       omit_duplicates=True)
    for bug_task in bug_tasks:
        if not bug_task.assignee:
            # remove the timezone info as it disturbs the calculation of the diff
            diff = today - bug_task.date_created.replace(tzinfo=None)
            inconsistent.append(common.BugReport(link=bug_task.web_link,
                                                 title=bug_task.bug.title,
                                                 age=diff.days))

    bug_tasks = lp_project.searchTasks(status=["New", "Confirmed", "Triaged"],
                                       omit_duplicates=True)
    for bug_task in bug_tasks:
        if bug_task.assignee:
            # remove the timezone info as it disturbs the calculation of the diff
            diff = today - bug_task.date_created.replace(tzinfo=None)
            inconsistent.append(common.BugReport(link=bug_task.web_link,
                                                 title=bug_task.bug.title,
                                                 age=diff.days))
    LOG.info("got inconsistent reports")
    return inconsistent

def main():
    print("Incomplete bug reports:")
    print("=======================")
    inconsistent_reports = get_inconsistent_reports()
    for r in sorted(inconsistent_reports, reverse=True):
        print(r)
    
    print("---------------------------------")
    print("%s inconsistent reports" % len(inconsistent_reports))

if __name__ == '__main__':
    main()