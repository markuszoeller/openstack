#!/usr/bin/env python

# Copyright 2016 Markus Zoeller
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

# ===========================================================================
# Creates the next IRC meeting dates for the wiki (call me lazy)
# ===========================================================================


import calendar
import datetime


WEEKDAY_NAME = "Tuesday"
TIME_WEEK_EVEN = "1800"
TIME_WEEK_ODD = "0800"
CHANNEL_NAME_EVEN = "openstack-meeting-4"
CHANNEL_NAME_ODD = "openstack-meeting-4"
WEEKS_NEXT = 3


meeting_slot = "* %(month)s %(day)s (%(weekday)s) %(time)s UTC, " \
               "<code>#%(channel_name)s</code> " \
               "(http://www.timeanddate.com/worldclock/fixedtime.html?" \
               "iso=%(isodate)sT%(time)s00)"


def next_weeks():
    d1 = datetime.datetime.utcnow()
    d2 = d1 + datetime.timedelta(weeks=WEEKS_NEXT)
    timespan = range((d2 - d1).days + 1)
    return (d1 + datetime.timedelta(days=i) for i in timespan)


def beautify_day(day):
    # NOTE: There has to be an easy way I didn't find...
    day = day.lstrip('0')
    if day.endswith("1") and int(day) != 11:
        return day + "st"
    elif day.endswith("2") and int(day) != 12:
        return day + "nd"
    elif day.endswith("3") and int(day) != 13:
        return day + "rd"
    else:
        return day + "th"


print('= Next meeting dates =')
print('')
for d in next_weeks():
    if calendar.day_name[d.weekday()] == WEEKDAY_NAME:
        week_number = d.isocalendar()[1]
        is_even_week = week_number % 2 == 0
        day = d.strftime('%d')
        day = beautify_day(day)
        month = d.strftime('%B')
        time = TIME_WEEK_EVEN if is_even_week else TIME_WEEK_ODD
        channel = CHANNEL_NAME_EVEN if is_even_week else CHANNEL_NAME_ODD
        iso_date = d.strftime('%Y%m%d')
        print(meeting_slot % {
            'day': day,
            'month': month,
            'time': time,
            'weekday': WEEKDAY_NAME,
            'isodate': iso_date,
            'channel_name': channel,
        })
        print('')
