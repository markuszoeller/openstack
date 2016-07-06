#!/usr/bin/env/python
#
# Queries OpenStack's Gerrit review system for merged bug fix changes and
# calculates the time it took to get them merged.
#

from datetime import datetime
import json
import requests


class MergedBugFixChange(object):

    def __init__(self, date_created, date_last_updated, change_id):
        fmt = "%Y-%m-%d %H:%M:%S"
        self.date_created = datetime.strptime(date_created[:-10], fmt)
        self.date_last_updated = datetime.strptime(date_last_updated[:-10], fmt)
        self.days_until_merged = (self.date_last_updated - self.date_created).days
        self.change_id = change_id

    def __str__(self):
        return "%s - (%sd)" % (self.change_id, self.days_until_merged)

    def __repr__(self):
        return str(self)

gerrit_url = "https://review.openstack.org/"
start = 0
# 500 = max internal paging size of gerrit
size = 500

changes = []
has_more_reviews = True


while has_more_reviews:
    has_more_reviews = False
    query = "project:openstack/nova" \
            "+status:merged" \
            "+NOT+age:365day" \
            "+message:closes-bug" \
            "+branch:master" \
            "&n=%s" \
            "&S=%s" % (size, start)
    review_url = gerrit_url + "/changes/?q=%s" % query
    response = requests.get(review_url)
    invalid_json = response.text
    valid_json = '\n'.join(invalid_json.split('\n')[1:])
    reviews = json.loads(valid_json)
    for r in reviews:
        change = MergedBugFixChange(r['created'], r['updated'], r['change_id'])
        changes.append(change)
        if '_more_changes' in r and r['_more_changes']:
            has_more_reviews = True
            start += size

def print_histogram(changes, interval=30):
    histo = {}
    for c in changes:
        timeframe = c.days_until_merged / interval + 1  # integer division
        if timeframe not in histo:
            histo[timeframe] = 1
        else:
            histo[timeframe] += 1
    for timeframe in sorted(histo.keys()):
        amount = histo[timeframe] * 100 / len(changes)
        print("~%d - #%d - ~%d%%" % (timeframe, histo[timeframe], amount))

print("histogram: %d changes - %d days interval" % (len(changes), 30))
print_histogram(changes, interval=30)

print("")
print("ten longest bug fixes")
for c in sorted(changes, key=lambda c: c.days_until_merged, reverse=True)[:10]:
    print(c)


