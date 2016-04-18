#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import datetime
import logging
import os

import common

PROJECT_NAME = "nova"
DAYS_SINCE_INCOMPLETE = 30
LOG = logging.getLogger(__name__)


def get_incomplete_reports():
    LOG.info("getting incomplete reports...")
    client = common.get_project_client(PROJECT_NAME)
    bug_tasks = client.searchTasks(status=["Incomplete"],
                                   omit_duplicates=True)
    
    today = datetime.datetime.today()
    reports = []
    
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_incomplete.replace(tzinfo=None)
        if diff.days > DAYS_SINCE_INCOMPLETE:
            reports.append(common.BugReport(link=bug_task.web_link,
                                     title=bug_task.bug.title,
                                     age=diff.days))
    LOG.info("got incomplete reports.")
    return reports


def main():
    print("potentially stale incomplete bug reports:")
    print("=========================================")
    reports = get_incomplete_reports()
    for r in sorted(reports, reverse=True):
        print(r)
    
    print("---------------------------------")
    print("%s bug reports" % len(reports))


if __name__ == '__main__':
    main()