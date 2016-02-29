#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import datetime
import json
import os
import requests

from launchpadlib.launchpad import Launchpad


PROJECT_NAME = "nova"
DAYS_SINCE_IN_PROGRESS = 14

cachedir = os.path.expanduser("~/.launchpadlib/cache/")
if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0700)
launchpad = Launchpad.login_anonymously('nova-bugs',
                                        'production', cachedir)

project = launchpad.projects[PROJECT_NAME]

bug_tasks = project.searchTasks(status=["In Progress"],
                                omit_duplicates=True)

def _remove_first_line(invalid_json):
    return '\n'.join(invalid_json.split('\n')[1:])

print("potentially stale bugs:")
print("=======================")
today = datetime.datetime.today()
counter = 0
counter_all = 0
for bug_task in sorted(bug_tasks, key=lambda bug_task: bug_task.date_in_progress):
    counter_all += 1
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_in_progress.replace(tzinfo=None)
    if diff.days > DAYS_SINCE_IN_PROGRESS:
        # TODO: this needs to be filtered if there are patches for review 
        gerrit_url="https://review.openstack.org/"
        review_url = gerrit_url + "/changes/?q=status:open+message:"+str(bug_task.bug.id)
        response = requests.get(review_url)
        reviews = json.loads(_remove_first_line(response.text))
        if not reviews:
            counter += 1
            print(bug_task.web_link + "  (" + str(diff.days) + " days since in progress)")
            
print("counter: " + str(counter))
print("counter_all: " + str(counter_all))
#             for review in reviews:
#                 review_url = gerrit_url + "changes/%s/detail" % review['id']
#                 response = requests.get(review_url)
#                 review_details = json.loads(_remove_first_line(response.text))
#                 print(review_details)
