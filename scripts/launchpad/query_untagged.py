#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which are untagedd
#
# Copyright 2016 Markus Zoeller

import datetime
import json
import os
import requests

from launchpadlib.launchpad import Launchpad


PROJECT_NAME = "nova"

cachedir = os.path.expanduser("~/.launchpadlib/cache/")
if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0700)
launchpad = Launchpad.login_anonymously('nova-bugs',
                                        'production', cachedir)

project = launchpad.projects[PROJECT_NAME]

bug_tasks = project.searchTasks(tags=["-*"],
                                status=["New"],
                                order_by="datecreated",
                                omit_duplicates=True)

print("untagged bug reports:")
print("=====================")
today = datetime.datetime.today()
for bug_task in bug_tasks:
    # remove the timezone info as it disturbs the calculation of the diff
    diff = today - bug_task.date_created.replace(tzinfo=None)
    print(bug_task.web_link + "  (" + str(diff.days) + " days old)")
