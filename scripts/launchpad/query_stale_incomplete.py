#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are potentially stale
# and in the "incomplete" state.
#
# Copyright 2016 Markus Zoeller

import datetime
import os
from launchpadlib.launchpad import Launchpad

PROJECT_NAME = "nova"
DAYS_SINCE_INCOMPLETE = 30

cachedir = os.path.expanduser("~/.launchpadlib/cache/")
if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0700)
launchpad = Launchpad.login_anonymously('nova-bugs',
                                        'production', cachedir)

project = launchpad.projects[PROJECT_NAME]

bug_tasks = project.searchTasks(status=["Incomplete"],
                                omit_duplicates=True)

print("potentially stale bugs:")
print("=======================")
today = datetime.datetime.today()
for bug_task in sorted(bug_tasks, key=lambda bug_task: bug_task.date_incomplete):
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_incomplete.replace(tzinfo=None)
    if diff.days > DAYS_SINCE_INCOMPLETE:
        print(bug_task.web_link + "  (" + str(diff.days) + " days since incomplete)")
