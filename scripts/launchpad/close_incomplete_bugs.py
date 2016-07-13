#!/usr/bin/env python
#
# Closes incomplete Launchpad bug reports
#
# Copyright 2016 Markus Zoeller

import argparse
import datetime
import logging
import os
import sys
import time

from launchpadlib.launchpad import Launchpad
import lazr.restfulclient.errors


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
logging.basicConfig(format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Close incomplete bug reports.")
parser.add_argument('project_name',
                    help='The Launchpad project name (nova, cinder, ...).')
parser.add_argument('--bugs', type=int, nargs='+',
                    help="The numbers of the bug reports to close.")
parser.add_argument('--verbose', '-v',
                    help='Enable debug logging.',
                    action="store_true")
parser.add_argument('--no-dry-run',
                    dest='no_dry_run',
                    help='Execute the expiration for real.',
                    action='store_true')
args = parser.parse_args()
LOG.info(args)


PROJECT_NAME = args.project_name
LOG.setLevel(logging.DEBUG if args.verbose else logging.INFO)


class BugReport(object):

    def __init__(self, link, title, age, bug_task):
        self.link = link
        self.title = title.encode('ascii', 'replace')
        self.age = age
        self.bug_task = bug_task

    def __str__(self):
        data = {'link': self.link, 'title': self.title, 'age': self.age}
        return "{link} ({title}) - ({age} days)".format(**data)

    def __cmp__(self, other):
        return cmp(self.age, other.age)


def get_project_client():
    cache_dir = os.path.expanduser("~/.launchpadlib/cache/")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, 0o700)

    def no_credential():
        LOG.error("Can't proceed without Launchpad credential.")
        sys.exit()

    launchpad = Launchpad.login_with(PROJECT_NAME + '-bugs',
                                     'production',
                                     cache_dir,
                                     credential_save_failed=no_credential)
    project = launchpad.projects[PROJECT_NAME]
    return project


def get_incomplete_reports(bug_numbers):
    LOG.info("getting incomplete reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(
        status=["Incomplete"],
        omit_duplicates=True,
        order_by="datecreated")

    today = datetime.datetime.today()
    expired = []
    matches = []

    for bug_task in bug_tasks:
        bug_number = bug_task.bug.id
        if bug_number not in bug_numbers:
            continue
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_created.replace(tzinfo=None)
        expired.append(BugReport(link=bug_task.web_link,
                                 title=bug_task.bug.title,
                                 age=diff.days,
                                 bug_task=bug_task))
        matches.append(bug_number)
    LOG.info("No matches found for: %s", set(bug_numbers) - set(matches))
    LOG.info("got %d incomplete reports." % len(expired))
    return expired


def close_bug_report(bug_report):
    subject = "Close incomplete bug report"
    comment = """
This bug lacks the necessary information to effectively reproduce and
fix it, therefore it has been closed. Feel free to reopen the bug by
providing the requested information and set the bug status back to "New".
"""
    bug_task = bug_report.bug_task
    bug_task.status = "Invalid"
    bug_task.assignee = None
    bug_task.importance = "Undecided"
    try:
        if args.no_dry_run:
            bug_task.lp_save()
            bug_task.bug.newMessage(subject=subject, content=comment)
        LOG.debug("closed bug report %s" % bug_report)
    except lazr.restfulclient.errors.ServerError as e:
        LOG.error(" - TIMEOUT during save ! (%s)" % e, end='')
    except Exception as e:
        LOG.error(" - ERROR during save ! (%s)" % e, end='')


def main():
    LOG.info("args: %s", args)
    if args.no_dry_run:
        LOG.info("This is not a drill! Bug reports will be closed for real!")
        time.sleep(4)  # in case you wanna ctrl-c this
    else:
        LOG.info("This is just a dry-run, nothing will happen.")
    expired_reports = get_incomplete_reports(args.bugs)
    LOG.info("starting closing...")
    for e in expired_reports:
        close_bug_report(e)
    LOG.info("closing done")


if __name__ == '__main__':
    LOG.info("starting script...")
    main()
    LOG.info("end script")
