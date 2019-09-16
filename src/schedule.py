from ics import Calendar, Event
import requests
from notify_run import Notify
import re
import os
from flask import redirect
from threading import Thread

MAIN_URL = os.environ.get('APP_RAPLA_URL')
ROOM_REGEX = '(\w\d{3}\w|\w\d{3})'
NOTIFICATION_TEXT = "Dein Vorlesungsplan hat sich geändert!"

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
    check_thr = Thread(target=check_notification, args=(uname,planname,course,new_cal))
    check_thr.start()
    return new_cal.__str__()

def create_notify_channel(directory):
    """Create a notify.run channel and return it's endpoint
    
    Arguments:
        directory {str} -- The directory
    
    Returns:
        str -- The notify.run endpoint
    """
    notify = Notify()
    notify.register()
    with open(directory, 'w') as f:
        f.write(notify.endpoint)
    return notify.endpoint

def read_existing_notifier(directory):
    """Read an existing norifier.run endpoint
    
    Arguments:
        directory {str} -- The directory
    
    Returns:
        str -- The endpoint
    """
    with open(directory) as f:
        return f.read()

def get_notifier_endpoint(directory):
    """Get the notifier.run endpoint for a filtered schedule
    
    Arguments:
        directory {str} -- The directory of the filtered schedule
    
    Returns:
        str -- The notify.run endpoint
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory = directory+"/notifyChannel"
    if os.path.exists(directory):
        return read_existing_notifier(directory)
    else:
        return create_notify_channel(directory)

def check_notification(uname, planname, course, new_cal):
    """Chack if a notification should be sent and send it if needed
    
    Arguments:
        uname {str} -- The creator of the RAPLA schedule
        planname {str} -- The name of the schedule
        course {str} -- The filtered course
        new_cal {ics.Calendar} -- The new ical object
    """
    directory = "./notifications/{}/{}/{}".format(uname,planname,course)
    new_cal_str = new_cal.__str__()

    # If the path does not exist yet
    if not os.path.exists(directory):
       os.makedirs(directory)
    
    # If an old calendar exists
    if os.path.exists(directory+"/calendar.ics"):
        with open(directory+"/calendar.ics") as f:
           data = f.read()
        # Check if change in calendar
        if new_cal_str.replace('\r','') != data:
            with open(directory+"/calendar.ics", 'w') as f:
                f.write(new_cal_str)
            # Send the notification
            send_notification(directory, NOTIFICATION_TEXT)
    else:
        # New calendar, send notification
        with open(directory+"/calendar.ics", 'w') as f:
            f.write(new_cal_str)
        send_notification(directory, NOTIFICATION_TEXT)

def send_notification(directory, text):
    """Sends a notification on a channel
    
    Arguments:
        directory {str} -- The directory of the channel
        text {str} -- The text to send
    """
    notify = Notify(endpoint=get_notifier_endpoint(directory))
    notify.send(text)

def get_notification_link(uname, planname, course):
    """Endpoint to redirect the User to the notification sign-up site
    
    Arguments:
        uname {str} -- The creator of the RAPLA schedule
        planname {str} -- The name of the schedule
        course {str} -- The filtered course
    
    Returns:
        flas.redirect -- A 302 redirect to the corresponding notify.run channel
    """
    directory = "./notifications/{}/{}/{}".format(uname,planname,course)
    #redirect_url = get_notifier_endpoint(directory).replace('notify.run/','notify.run/c/')
    redirect_url = "https://rapla.baswag.de"
    print(redirect_url)
    return redirect(redirect_url)