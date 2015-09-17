#!/usr/bin/env python

# Displays all Launchpad bugs for OpenStack/Nova which block
# the creation of the release candidate.
#
# Copyright 2015 Markus Zoeller

import os
from launchpadlib.launchpad import Launchpad


cachedir = os.path.expanduser("~/.launchpadlib/cache/")
if not os.path.exists(cachedir):
    os.makedirs(cachedir, 0700)
launchpad = Launchpad.login_anonymously('just testing',
                                        'production', cachedir)

project = launchpad.projects["nova"]

bug_tasks = project.searchTasks(tags=["liberty-rc-potential"],
                                order_by='-datecreated',
                                omit_duplicates=True)

print "================================================="
print "Bugs (\"liberty-rc-potential\") "
print "================================================="
for bug_task in bug_tasks:
    print "https://bugs.launchpad.net/nova/+bug/" + str(bug_task.bug.id)

print "================================================="
print "Reviews"
print "================================================="
link = "https://review.openstack.org/#/q/"
link += "status:open+project:openstack/nova"
link += "+(nil"
for bug_task in bug_tasks:
    link += "+OR+message:\"#" + str(bug_task.bug.id) + "\""
link += "+),n,z"
print link
