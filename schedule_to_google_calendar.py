from __future__ import print_function
import httplib2
import os
import time
from datetime import datetime
import re

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from bs4 import BeautifulSoup

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def ftch_data(s, word, dot):
    semicoloms = re.findall('\([^\)]*\)', s)
    types = semicoloms[0]
    subject = (s[s.find(')') + 2:s.find(word) - 1])
    indices = [i for i, x in enumerate(s) if x == "."]
    teachers = (s[s.find(word):indices[dot] - 2])
    auditori = (s[indices[dot] - 1:])
    if len(semicoloms) > 1:
        potok = semicoloms[1]
        auditori = auditori[:auditori.index(potok) - 1]
    return types, subject, teachers, auditori


def parse_string(s):
    if 'асистент' in s:
        return ftch_data(s, 'асистент', 2)
    elif 'доцент' in s:
        return ftch_data(s, 'доцент', 2)
    elif 'ст. викладач' in s:
        return ftch_data(s, 'ст. викладач', 3)
    elif 'викладач' in s:
        return ftch_data(s, 'викладач', 2)


soup = BeautifulSoup(open("try/html/allllll.html"), "html.parser")

table = soup.find_all('table')
h4 = soup.find_all('h4')[3:]

d = {'Понеділок': 1, 'Вівторок': 2, 'Середа': 3, 'Четвер': 4, "П'ятниця": 5}

di = {'1': {'start': {'h': 8, 'm': 30}, 'end': {'h': 9, 'm': 50}},
      '2': {'start': {'h': 10, 'm': 0}, 'end': {'h': 11, 'm': 20}},
      '3': {'start': {'h': 11, 'm': 50}, 'end': {'h': 13, 'm': 10}},
      '4': {'start': {'h': 13, 'm': 20}, 'end': {'h': 14, 'm': 40}},
      '5': {'start': {'h': 14, 'm': 50}, 'end': {'h': 16, 'm': 10}},
      '6': {'start': {'h': 16, 'm': 20}, 'end': {'h': 17, 'm': 40}},
      '7': {'start': {'h': 17, 'm': 50}, 'end': {'h': 19, 'm': 10}},
      '8': {'start': {'h': 19, 'm': 20}, 'end': {'h': 20, 'm': 40}}}


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)

    return credentials


def main():
    credentials = get_credentials()
    print(credentials, 'credentials')
    http = credentials.authorize(httplib2.Http())
    print(http, 'http')
    service = discovery.build('calendar', 'v3', http=http)
    print(service, 'service')

    calendar = {
        'summary': 'All from html',
        'timeZone': 'Europe/Kiev'
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    calendarId = created_calendar['id']
    print(created_calendar)
    print(calendarId)

    for timetable, date in zip(table, h4):
        lesson_info = timetable.find_all('td')[1::2]
        lesson_date = date.find(text=True, recursive=False)
        for i, info in enumerate(lesson_info):
            if info.text:
                types, subject, teacher, classroom = parse_string(info.text)
                print(i + 1, ' пара', info.text)
                d = [int(s) for s in lesson_date.split('.')]
                start = datetime(d[2], d[1], d[0], di[str(i + 1)]['start']['h'],
                                 di[str(i + 1)]['start']['m']).isoformat()
                end = datetime(d[2], d[1], d[0], di[str(i + 1)]['end']['h'],
                               di[str(i + 1)]['end']['m']).isoformat()

                event = {
                    'summary': types + ' ' + subject,
                    'location': classroom,
                    'description': teacher,
                    'start': {
                        'dateTime': start,
                        'timeZone': 'Europe/Kiev',
                    },
                    'end': {
                        'dateTime': end,
                        'timeZone': 'Europe/Kiev',
                    }
                }

                event = service.events().insert(calendarId=calendarId, body=event).execute()
                print('Event created: %s' % (event.get('htmlLink')))

        time.sleep(5)


if __name__ == '__main__':
    main()
