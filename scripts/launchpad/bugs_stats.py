#!/usr/bin/env/python
#
# Creates a HTML file which can be used as a dashboard for
# cleanup tasks of the bug management.
#

import datetime
import json
import os
import requests
import logging

from jinja2 import Environment, FileSystemLoader
from launchpadlib.launchpad import Launchpad

RECENT_ACTIVITY_IN_DAYS = 14

LOG_FORMAT="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_NAME = "nova"

ALL_STATES = ["Incomplete", "Confirmed", "Won't Fix", "Opinion",
              "Invalid", "Fix Released"]

LOG = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class StatSummary(object):
    
    def __init__(self, person_url, person_name):
        self.person_url = person_url.encode('ascii', 'replace')
        self.person_name = person_name.encode('ascii', 'replace')
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
        return "<StatSummary: person=%(person)s, " \
               "confirmed=%(confirmed)d, rejected=%(rejected)d, " \
               "resolved=%(resolved)d, inquired=%(inquired)d, " \
               "sum=%(sum)d>" % \
                {
                    'person': self.person_name,
                    'confirmed': len(self.confirmed_reports),
                    'rejected': len(self.rejected_reports),
                    'resolved': len(self.resolved_reports),
                    'inquired': len(self.inquired_reports),
                    'sum': self.sum
                }

    @property
    def sum(self):
        return int(len(self.confirmed_reports) + \
               len(self.rejected_reports) + \
               len(self.resolved_reports) + \
               len(self.inquired_reports))

def get_project_client():
    cache_dir = os.path.expanduser("~/.launchpadlib/cache/")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, 0o700)
    launchpad = Launchpad.login_anonymously(PROJECT_NAME + '-bugs-stats',
                                            'production',
                                            cache_dir)
    project = launchpad.projects[PROJECT_NAME]
    return project

def get_recent_actions():
    LOG.info("querying recent bug triage actions ...")
    project = get_project_client()
    bug_tasks = project.searchTasks(status=ALL_STATES,
                                    order_by='-date_last_updated',
                                    omit_duplicates=False)
    today = datetime.datetime.today()
    stats = {}
    
    def get_summary(person):
        link = "?? unknown ??"
        name = "?? unknown ??"
        if person:
            link = person.web_link.encode('ascii', 'replace')
            name = person.display_name.encode('ascii', 'replace')
        if not link in stats.keys():
            stats[link] = StatSummary(link, name)
        return stats[link]
    
    def is_rejected(a):
        return a.newvalue in ["Invalid", "Opinion", "Won't Fix"]
    
    def is_new_confirmed(a, bug_task):
        return a.newvalue == 'Confirmed' and a.oldvalue == "New" and \
            a.person != bug_task.owner
    
    def is_trackable_status_change(a):
        return a.whatchanged == "nova: status" and \
               a.newvalue in ["Incomplete", "Confirmed", "Won't Fix",
                              "Opinion", "Invalid", "Fix Released"]
    
    def is_infra(person):
        return person.web_link.encode('ascii', 'replace') == \
            "https://launchpad.net/~hudson-openstack"
    
    for bug_task in bug_tasks:
        diff = today - bug_task.bug.date_last_updated.replace(tzinfo=None)
        if diff.days > RECENT_ACTIVITY_IN_DAYS:
            break
    
        for a in bug_task.bug.activity:
            diff = today - a.datechanged.replace(tzinfo=None)
            if diff.days > RECENT_ACTIVITY_IN_DAYS:
                # ignore activities which are not recent
                continue

            person = a.person
            web_link = bug_task.web_link.encode('ascii', 'replace')

            if is_trackable_status_change(a):
                if is_rejected(a):
                    get_summary(person).rejected_reports.append(web_link)
                elif is_new_confirmed(a, bug_task):
                    get_summary(person).confirmed_reports.append(web_link)
                elif a.newvalue == 'Fix Released':
                    if is_infra(person):
                        person = bug_task.assignee if bug_task.assignee else person
                    get_summary(person).resolved_reports.append(web_link)
                elif a.newvalue == "Incomplete" or \
                    a.whatchanged == "marked as duplicate":
                    get_summary(person).inquired_reports.append(web_link)
    
    LOG.info("queried recent bug triage actions.")
    return stats.values()


def create_html_dashboard():
    LOG.info("creating html dashboard...")
    d = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    
    recent_actions = get_recent_actions()
    for r in recent_actions:
        LOG.info(r)
    
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),
                         trim_blocks=True,
                         autoescape=True)
    template = "bugs_stats_template.html"
    rendered_html = j2_env.get_template(template).render(
        last_update=d,
        recent_days=RECENT_ACTIVITY_IN_DAYS,
        recent_actions=sorted(recent_actions),
    )
    with open("bugs-stats.html", "wb") as fh:
        fh.write(rendered_html)
    LOG.info("created html dashboard")

if __name__ == '__main__':
    LOG.info("starting script...")
    create_html_dashboard()
    LOG.info("end script")
