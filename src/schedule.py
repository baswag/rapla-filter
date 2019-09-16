from ics import Calendar, Event
import requests
import re
import os
from threading import Thread
import notification

MAIN_URL = os.environ.get('APP_RAPLA_URL')
ROOM_REGEX = '(\w\d{3}\w|\w\d{3})'


def read_plain(uname, planname):
    """Reads and returns the plain RAPLA schedule
    
    Arguments:
        uname {str} -- The RAPLA schedule creator
        planname {str} -- The name of the schedule
    
    Returns:
        str -- The ical string from RAPLA
    """
    r = requests.get(MAIN_URL.format(uname,planname))
    return r.text

def read_filtered(uname, planname, course):
    """Reads and filters a RAPLA schedule
    
    Arguments:
        uname {str} -- The RAPLA schedule creator
        planname {str} -- The name of the schedule
        course {str} -- The course to filter
    
    Returns:
        str -- The filtered ical string
    """
    # Read the plain ical
    ical = read_plain(uname, planname)
    c = Calendar(ical)
    events = c.events
    new_events = []
    # Iterate over all events
    for event in events:
        # Skip events not for selected course
        if course not in event.location:
            continue
        # Find all rooms for event and construct the new location string
        rooms = re.findall(ROOM_REGEX,event.location)
        room_str = ""
        for room in rooms:
            room_str += room + ", "
        room_str = room_str[:-2]
        event.location = room_str
        new_events.append(event)
    # Create the new Calendar
    new_cal = Calendar(events=new_events, creator=c.creator)
    # Run async as to not block main Thread
    check_thr = Thread(target=notification.check_notification, args=(uname,planname,course,new_cal))
    check_thr.start()
    return new_cal.__str__()
