#!/usr/bin/env python
#
# Closes bug reports which are old and
#
# Copyright 2016 Markus Zoeller


from launchpadlib.launchpad import Launchpad

import datetime
import logging
import os

PROJECT_NAME = "nova"

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)

DAYS_SINCE_CREATED = 30 * 18  # 18 months
STILL_VALID_FLAG = "CONFIRMED FOR: %(release_name)s"  # UPPER CASE
SUPPORTED_RELEASE_NAMES = []


class BugReport(object):

    def __init__(self, link, title, age):
        self.link = link
        self.title = title.encode('ascii', 'replace')
        self.age = age

    def __str__(self):
        data = {'link': self.link, 'title': self.title, 'age': self.age}
        return "{link} ({title}) - ({age} days)".format(**data)

    def __cmp__(self, other):
        return cmp(self.age, other.age)


def get_project_client():
    cache_dir = os.path.expanduser("~/.launchpadlib/cache/")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, 0o700)
    launchpad = Launchpad.login_anonymously(PROJECT_NAME + '-bugs',
                                            'production', cache_dir)
    project = launchpad.projects[PROJECT_NAME]
    return project


def fill_supported_release_names():
    LOG.info("filling supported release names...")
    lp_project = get_project_client()
    # master name
    SUPPORTED_RELEASE_NAMES.append(lp_project.development_focus.name)
    for s in lp_project.series:
        if s.active:
            # stable branch names
            SUPPORTED_RELEASE_NAMES.append(s.name)
    LOG.info("filled supported release names: %s", SUPPORTED_RELEASE_NAMES)


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

    def bug_is_still_valid(bug):
        for message in bug.messages:
            for release_name in SUPPORTED_RELEASE_NAMES:
                flag = STILL_VALID_FLAG % \
                       {'release_name': release_name.upper()}
                if flag in message.content:
                    return True
        return False

    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_created.replace(tzinfo=None)
        if diff.days < DAYS_SINCE_CREATED:
            break
        if bug_is_still_valid(bug_task.bug):
            continue
        expired.append(BugReport(link=bug_task.web_link,
                                 title=bug_task.bug.title,
                                 age=diff.days))
    LOG.info("got potentially expired reports.")
    return expired


def expire_bug_report(bug_report):
    LOG.debug(bug_report)


def main():
    fill_supported_release_names()
    expired_reports = get_expired_reports()
    for e in expired_reports:
        expire_bug_report(e)


if __name__ == '__main__':
    LOG.info("starting script...")
    main()
    LOG.info("end script")
