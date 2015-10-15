#!/usr/bin/env python

# Copyright 2015 Markus Zoeller <mzoeller@de.ibm.com>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys

from launchpadlib.launchpad import Launchpad

# +-----+ 1         1..* +----------+
# | bug +----------------> bug_task |
# +--+--+                +-----+----+
#    |                         |
#    |                         |
#    |       +---------+       |
#    +-------> project <-------+
#       1..* +---------+ 1
#
# One bug has at least 1 bug_task.
# One bug_task belongs to exactly one bug.
# One bug can affect multiple projects
# One bug_task is specific to one project

# Launchpad statuses
# "New", "Incomplete", "Incomplete (with response)",
# "Incomplete (without response)", "Confirmed", "Triaged",
# "In Progress", "Fix Committed", "Fix Released",
# "Invalid", "Won't Fix", "Opinion"


class LaunchpadClient(object):
    '''
    A facade for the launchpadlib to make access easier
    '''

    def __init__(self):
        self._create_launchpad_client()

    def _create_launchpad_client(self):
        cachedir = os.path.expanduser("~/.launchpadlib/cache/")
        if not os.path.exists(cachedir):
            os.makedirs(cachedir, 0700)
        self.launchpad = Launchpad.login_anonymously('bug-triage',
                                                     'production', cachedir)

    def get_bug_tasks_by_states(self, project_name, states):
        ''' Return the launchpad bugs by states

        :param project_name: The name of the launchpad project (e.g. 'nova')
        :param states: A list of launchpad states (e.g. ['New', 'Invalid'])
        '''
        project = self.get_project(project_name)
        bug_tasks = project.searchTasks(status=states, omit_duplicates=True)
        return bug_tasks

    def get_project(self, project_name):
        ''' Return the launchpad project by name

        :param project_name: The name of the launchpad project (e.g. 'nova')
        '''
        project = self.launchpad.projects[project_name]
        return project


def main():
    client = LaunchpadClient()

    print "fetching bugs from Launchpad..."
    tasks = client.get_bug_tasks_by_states("nova", ["New"])

    print "processing bugs and counting subteam tags..."
    # use dict to allow counting { tag_x: count, tag_y: count }
    tags_counter = {}
    for task in tasks:
        try:
            tags = task.bug.tags
            for tag in tags:
                if tag in tags_counter:
                    tags_counter[tag] += 1
                else:
                    tags_counter[tag] = 1
        except TypeError, e:
            print "ignore task %s because %s" % (task.bug.id, e)

    print "sorting subteam tags by bug-count..."
    # make tuples to sort them later (count, tag)
    counted = []
    for tag in tags_counter:
        counted.append((tags_counter[tag], tag))

    print "processed subteam bug tags:"
    print "==========================="
    # from highest count to the lowest count
    for t in sorted(counted, reverse=True):
        print "subteam: %s : %d" % (t[1], t[0])
    print "===== %d untriaged bugs =======" % len(counted)

if __name__ == '__main__':
    sys.exit(main())
