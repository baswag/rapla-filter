from pyfcm import FCMNotification
import pickle
import urllib.parse
import os
from flask import redirect
push_service = FCMNotification(api_key=os.environ.get("APP_FCM_KEY"))

NOTIFICATION_TITLE = "RAPLA Update"
NOTIFICATION_TEXT = "Dein Vorlesungsplan hat sich geändert!"

def check_notification(uname, planname, course, new_cal):
    """Chack if a notification should be sent and send it if needed

    Arguments:
        uname {str} -- The creator of the RAPLA schedule
        planname {str} -- The name of the schedule
        course {str} -- The filtered course
        new_cal {ics.Calendar} -- The new ical object
    """
    directory = "./notifications/{}/{}/{}".format(uname, planname, course)
    new_cal_str = new_cal.__str__()

    # If the path does not exist yet
    if not os.path.exists(directory):
        os.makedirs(directory)

    # If an old calendar exists
    if os.path.exists(directory+"/calendar.ics"):
        with open(directory+"/calendar.ics") as f:
            data = f.read()
        # Check if change in calendar
        if new_cal_str.replace('\r', '') == data:
            with open(directory+"/calendar.ics", 'w') as f:
                f.write(new_cal_str)
            # Send the notification
            send_notification(uname, planname, course, NOTIFICATION_TEXT)
    else:
        # New calendar, send notification
        with open(directory+"/calendar.ics", 'w') as f:
            f.write(new_cal_str)
        send_notification(uname, planname, course, NOTIFICATION_TEXT)


def send_notification(uname, planname, course, text):
    """Sends a notification on a channel

    Arguments:
        COMMON ARGUMENTS
        text {str} -- The text to send
    """
    directory = "./notifications/{}/{}/{}".format(uname, planname, course)
    try:
        with open(directory+"/subscribers", "rb") as f:
            subscribers = pickle.load(f)
        print(push_service.notify_multiple_devices(message_body=NOTIFICATION_TEXT,
                                                   message_title=NOTIFICATION_TITLE, registration_ids=subscribers))
    except FileNotFoundError:
        print("No subscribers for this course")
    except Exception as e:
        print("Exception while sending notification: {}".format(e.__str__()))


def get_notification_link(uname, planname, course):
    """Endpoint to redirect the User to the notification sign-up site

    Arguments:
        COMMON ARGUMENTS

    Returns:
        flask.redirect -- A 302 redirect to the corresponding notify.run channel
    """
    print("Redirecting Notification Request")
    directory = "./notifications/{}/{}/{}".format(uname, planname, course)

    if not os.path.exists(directory):
        os.makedirs(directory)
    redirect_url = "/?uname={}&planname={}&course={}".format(
        uname, planname, course)
    return redirect(redirect_url, code=302)


def subscribe_to_notification(uname, planname, course, token):
    """Subscribes to a Notification for a course
    
    Arguments:
        COMMON ARGUMENTS
        token {str} -- The FCM Client Token
    """
    token = urllib.parse.unquote(token)
    planname = planname.replace("+", "%2B")
    directory = "./notifications/{}/{}/{}/subscribers".format(
        uname, planname, course)
    l = []
    try:
        with open(directory, "rb") as f:
            l = pickle.load(f)
    except Exception:
        open(directory, "ab").close()
    text = "Benachrichtigungen für {} ".format(course)
    if token not in l:
        l.append(token)
        with open(directory, "wb") as f:
            pickle.dump(l, f)

        push_service.notify_single_device(
            registration_id=token, message_body=text+"abboniert", message_title=NOTIFICATION_TITLE)
    else:
        l.remove(token)
        with open(directory, "wb") as f:
            pickle.dump(l, f)
        push_service.notify_single_device(
            registration_id=token, message_body=text+"abbestellt", message_title=NOTIFICATION_TITLE)


def get_notification_status(uname, planname, course, token):
    """Returns the status of the subscription
    
    Arguments:
        COMMON ARGUMENTS
        token {str} -- The FCM Client Token
    
    Returns:
        bool -- Is this token subscribed?
    """
    token = urllib.parse.unquote(token)
    planname = planname.replace("+", "%2B")
    directory = "./notifications/{}/{}/{}/subscribers".format(
        uname, planname, course)
    result = False
    try:
        l = []
        with open(directory, "rb") as f:
            l = pickle.load(f)
        if token in l:
            result = True
    except:
        pass
    return result
