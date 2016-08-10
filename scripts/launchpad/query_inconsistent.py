#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import argparse
import datetime
import logging

import common

parser = argparse.ArgumentParser()
parser.add_argument('-p',
                    '--project-name',
                    required=True,
                    dest='project_name',
                    help='The LP project name.')

args = parser.parse_args()

PROJECT_NAME = args.project_name

LOG = logging.getLogger(__name__)


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
    print("Inconsistent bug reports:")
    print("=======================")
    inconsistent_reports = get_inconsistent_reports()
    for r in sorted(inconsistent_reports, reverse=True):
        print(r)
    
    print("---------------------------------")
    print("%s inconsistent reports" % len(inconsistent_reports))

if __name__ == '__main__':
    main()