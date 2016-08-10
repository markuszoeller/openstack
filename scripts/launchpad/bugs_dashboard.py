#!/usr/bin/env/python
#
# Creates a HTML file which can be used as a dashboard for
# cleanup tasks of the bug management.
#

import argparse
import datetime
import json
import os
import requests
import logging

from jinja2 import Environment, FileSystemLoader
from launchpadlib.launchpad import Launchpad

parser = argparse.ArgumentParser()
parser.add_argument('-p',
                    '--project-name',
                    required=True,
                    dest='project_name',
                    help='The LP project name.')

args = parser.parse_args()

PROJECT_NAME = args.project_name

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DAYS_SINCE_INCOMPLETE = 30
DAYS_SINCE_IN_PROGRESS = 14
DAYS_SINCE_RECENT = 10
DAYS_OLD_WISHLIST = 365
LP_OPEN_STATES = ["New", "Incomplete", "Confirmed", "Triaged", "In Progress"]

DAYS_SINCE_CREATED = 30 * 18  # 18 months
STILL_VALID_FLAG = "CONFIRMED FOR: %(release_name)s"  # UPPER CASE

SUPPORTED_RELEASE_NAMES = []

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
formatter = logging.Formatter(LOG_FORMAT)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
LOG = logging.getLogger(__name__)
LOG.addHandler(stream_handler)
LOG.setLevel(logging.INFO)


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


def get_recent_reports():
    LOG.info("getting recent reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=LP_OPEN_STATES,
                                       omit_duplicates=True,
                                       order_by="-datecreated")
    today = datetime.datetime.today()
    recent_reports = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_created.replace(tzinfo=None)
        if diff.days <= DAYS_SINCE_RECENT:
            recent_reports.append(BugReport(link=bug_task.web_link,
                                            title=bug_task.bug.title,
                                            age=diff.days))
        else:
            break
    LOG.info("got recent reports")
    return recent_reports


def get_undecided():
    LOG.info("getting undecided reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["Confirmed", "Triaged"],
                                       importance="Undecided",
                                       omit_duplicates=True,
                                       order_by="-datecreated")
    today = datetime.datetime.today()
    undecided = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_created.replace(tzinfo=None)
        undecided.append(BugReport(link=bug_task.web_link,
                                   title=bug_task.bug.title,
                                   age=diff.days))
    LOG.info("got undecided reports")
    return undecided


def get_fix_committed():
    LOG.info("getting fix committed reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["Fix Committed"],
                                       omit_duplicates=True)
    today = datetime.datetime.today()
    fix_committed = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_fix_committed.replace(tzinfo=None)
        fix_committed.append(BugReport(link=bug_task.web_link,
                                       title=bug_task.bug.title,
                                       age=diff.days))
    LOG.info("got fix committed reports")
    return fix_committed


def get_stale_incomplete():
    LOG.info("getting stale incomplete reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["Incomplete"],
                                       omit_duplicates=True)
    today = datetime.datetime.today()
    stale_bug_reports = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_incomplete.replace(tzinfo=None)
        if diff.days <= DAYS_SINCE_INCOMPLETE:
            continue
        stale_bug_reports.append(BugReport(link=bug_task.web_link,
                                           title=bug_task.bug.title,
                                           age=diff.days))
    LOG.info("got stale incomplete reports")
    return stale_bug_reports


def get_patched_reports():
    LOG.info("getting patched reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["New", "Confirmed", "Triaged"],
                                       has_patch=True,
                                       omit_duplicates=True)
    today = datetime.datetime.today()
    patched_reports = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_created.replace(tzinfo=None)
        patched_reports.append(BugReport(link=bug_task.web_link,
                                         title=bug_task.bug.title,
                                         age=diff.days))
    LOG.info("got patched reports")
    return patched_reports


def get_incomplete_response():
    LOG.info("getting incomplete with response reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["Incomplete (with response)"],
                                       omit_duplicates=True)
    today = datetime.datetime.today()
    incomplete_response = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_incomplete.replace(tzinfo=None)
        incomplete_response.append(BugReport(link=bug_task.web_link,
                                             title=bug_task.bug.title,
                                             age=diff.days))
    LOG.info("got incomplete with response reports")
    return incomplete_response


def get_inconsistent_reports():
    LOG.info("getting inconsistent reports...")
    inconsistent = []
    today = datetime.datetime.today()
    lp_project = get_project_client()

    bug_tasks = lp_project.searchTasks(status=["In Progress"],
                                       omit_duplicates=True)
    for bug_task in bug_tasks:
        if not bug_task.assignee:
            # remove the timezone info as it disturbs the calculation of the diff
            diff = today - bug_task.date_created.replace(tzinfo=None)
            inconsistent.append(BugReport(link=bug_task.web_link,
                                          title=bug_task.bug.title,
                                          age=diff.days))

    bug_tasks = lp_project.searchTasks(status=["New", "Confirmed", "Triaged"],
                                       omit_duplicates=True)
    for bug_task in bug_tasks:
        if bug_task.assignee:
            # remove the timezone info as it disturbs the calculation of the diff
            diff = today - bug_task.date_created.replace(tzinfo=None)
            inconsistent.append(BugReport(link=bug_task.web_link,
                                          title=bug_task.bug.title,
                                          age=diff.days))
    LOG.info("got inconsistent reports")
    return inconsistent


def get_old_wishlist():
    LOG.info("getting old wishlist reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["New", "Confirmed", "Triaged"],
                                       importance="Wishlist",
                                       omit_duplicates=True)
    today = datetime.datetime.today()
    old_wishlist = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_created.replace(tzinfo=None)
        if diff.days > DAYS_OLD_WISHLIST:
            old_wishlist.append(BugReport(link=bug_task.web_link,
                                          title=bug_task.bug.title,
                                          age=diff.days))
    LOG.info("got old wishlist reports")
    return old_wishlist


def get_expired_reports():
    LOG.info("getting potentially expired reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["New", "Confirmed", "Triaged"],
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


def get_stale_in_progress():
    LOG.info("getting stale in progress reports...")
    lp_project = get_project_client()
    bug_tasks = lp_project.searchTasks(status=["In Progress"],
                                       omit_duplicates=True)
    today = datetime.datetime.today()
    stale_bug_reports = []
    for bug_task in bug_tasks:
        # remove the timezone info as it disturbs the calculation of the diff
        diff = today - bug_task.date_in_progress.replace(tzinfo=None)
        if diff.days <= DAYS_SINCE_IN_PROGRESS:
            continue
        if bug_has_open_changes(bug_task.bug.id):
            continue
        stale_bug_reports.append(BugReport(link=bug_task.web_link,
                                           title=bug_task.bug.title,
                                           age=diff.days))
    LOG.info("got stale in progress reports")
    return stale_bug_reports


def bug_has_open_changes(bug_id):
    gerrit_url = "https://review.openstack.org/"
    review_url = gerrit_url + "/changes/?q=status:open+message:"+str(bug_id)
    response = requests.get(review_url)
    reviews = json.loads(remove_first_line(response.text))
    return reviews


def remove_first_line(invalid_json):
    return '\n'.join(invalid_json.split('\n')[1:])


def create_html_dashboard():
    LOG.info("creating html dashboard...")
    fill_supported_release_names()
    d = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True,
                         autoescape=True)
    template = "bugs_dashboard_template.html"
    rendered_html = j2_env.get_template(template).render(
        last_update=d,
        stale_incomplete=sorted(get_stale_incomplete(), reverse=True),
        stale_in_progress=sorted(get_stale_in_progress(), reverse=True),
        recent_reports=sorted(get_recent_reports(), reverse=True),
        undecided_reports=sorted(get_undecided(), reverse=True),
        fix_committed=sorted(get_fix_committed(), reverse=True),
        incomplete_response=sorted(get_incomplete_response(), reverse=True),
        patched_reports=sorted(get_patched_reports(), reverse=True),
        old_wishlist=sorted(get_old_wishlist(), reverse=True),
        inconsistent_reports=sorted(get_inconsistent_reports(), reverse=True),
        expired_reports=sorted(get_expired_reports(), reverse=True)
    )
    with open("bugs-dashboard.html", "wb") as fh:
        fh.write(rendered_html)
    LOG.info("created html dashboard")

if __name__ == '__main__':
    LOG.info("starting script...")
    create_html_dashboard()
    LOG.info("end script")
