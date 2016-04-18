#!/usr/bin/env python
#
# Common client code
#
# Copyright 2016 Markus Zoeller

import os

from launchpadlib.launchpad import Launchpad

def get_project_client(project_name):
    cachedir = os.path.expanduser("~/.launchpadlib/cache/")
    if not os.path.exists(cachedir):
        os.makedirs(cachedir, 0o700)
    launchpad = Launchpad.login_anonymously(project_name + '-bugs',
                                            'production', cachedir)
    project = launchpad.projects[project_name]
    return project

def remove_first_line(invalid_json):
    return '\n'.join(invalid_json.split('\n')[1:])

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