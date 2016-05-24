#!/usr/bin/env python
#
# Closes Launchpad bug reports which are older than the oldest stable
# release (usually 18 months).
#
# Copyright 2016 Markus Zoeller
# Copyright 2016 Steven Hardy

import datetime
import logging
import os

from launchpadlib.launchpad import Launchpad
import lazr.restfulclient.errors

# TODO(markus_z): make that an arg
PROJECT_NAME = "nova"

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
# TODO(markus_z): make the project name an arg
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

DAYS_SINCE_CREATED = 30 * 18  # 18 months
STILL_VALID_FLAG = "CONFIRMED FOR: %(release_name)s"  # UPPER CASE
SUPPORTED_RELEASE_NAMES = []  # UPPER CASE


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
    # TODO(markus_z) login with credentials
    launchpad = Launchpad.login_anonymously(PROJECT_NAME + '-bugs',
                                            'production', cache_dir)
    project = launchpad.projects[PROJECT_NAME]
    return project


def fill_supported_release_names():
    LOG.info("filling supported release names...")
    lp_project = get_project_client()
    for s in lp_project.series:
        if s.active:
            # stable branch names
            SUPPORTED_RELEASE_NAMES.append(s.name.upper())
    # master name
    SUPPORTED_RELEASE_NAMES.append(lp_project.development_focus.name.upper())
    LOG.info("filled supported release names: %s", SUPPORTED_RELEASE_NAMES)


def bug_is_still_valid(bug):
    for message in bug.messages:
        for release_name in SUPPORTED_RELEASE_NAMES:
            flag = STILL_VALID_FLAG % {'release_name': release_name}
            if flag in message.content:
                return True
    return False


def get_expired_reports():
    LOG.info("getting potentially expired reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(
        status=["New", "Confirmed", "Triaged"],
        importance=["Unknown", "Undecided", "Critical", "High", "Medium",
                    "Low"],  # ignore 'wishlist'; they get special treatment
        omit_duplicates=True,
        order_by="datecreated")
    today = datetime.datetime.today()
    expired = []

    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_created.replace(tzinfo=None)
        if diff.days < DAYS_SINCE_CREATED:
            break
        if bug_is_still_valid(bug_task.bug):
            continue
        expired.append(BugReport(link=bug_task.web_link,
                                 title=bug_task.bug.title,
                                 age=diff.days,
                                 bug_task=bug_task))
    LOG.info("got %d potentially expired reports." % len(expired))
    return expired


def expire_bug_report(bug_report):
    subject = "Cleanup EOL bug report"
    comment = """
This is an automated cleanup. This bug report got closed because it
is older than %(mm)d months and there is no open code change to fix this.
After this time it is unlikely that the circumstances which lead to
the observed issue can be reproduced.

If you can reproduce it, please:
* reopen the bug report (set to status "New")
* AND add the steps to reproduce the issue (if applicable)
* AND leave a comment "CONFIRMED FOR: <RELEASE_NAME>"
  Only still supported release names are valid (%(supported_releases)s).
  Valid example: CONFIRMED FOR: %(valid_release_name)s
""" % {'mm': DAYS_SINCE_CREATED / 30,
       'supported_releases': ', '.join(SUPPORTED_RELEASE_NAMES),
       'valid_release_name': SUPPORTED_RELEASE_NAMES[0]}

    bug_task = bug_report.bug_task
    # bug_task.bug.newMessage(subject=subject, content=comment)
    bug_task.status = "Won't Fix"
    bug_task.assignee = None
    bug_task.importance = "Undecided"
    try:
        # bug_task.lp_save()
        LOG.debug("expired bug report %s" % bug_report)
        LOG.debug("message: %s" % comment)
    except lazr.restfulclient.errors.ServerError as e:
        LOG.error(" - TIMEOUT during save ! (%s)" % e, end='')
    except Exception as e:
        LOG.error(" - ERROR during save ! (%s)" % e, end='')


def main():
    fill_supported_release_names()
    expired_reports = get_expired_reports()
    LOG.info("starting expiration...")
    for e in expired_reports:
        expire_bug_report(e)
    LOG.info("expiration done")


if __name__ == '__main__':
    LOG.info("starting script...")
    main()
    LOG.info("end script")
