from __future__ import print_function
import httplib2
import os
import sys
import boto3
import json
import logging

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

def handler(event, context):
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
  logging.warning("Request recieved")
  logging.warning(event)
  SCOPES = 'https://www.googleapis.com/auth/calendar'
  CLIENT_SECRET_FILE = 'client_secret.json'
  APPLICATION_NAME = 'Google Calendar API Python Quickstart'
  logging.warning(event)
  if(event['request']['dialogState']== "COMPLETED"):
    isResourseAvailable = getResourceAvailability(event)
    if(isResourseAvailable):
       eventResult = createEvent(event)
       eventSummary = eventResult.get('summary')
       response = {
                    "version": "1.0",
                    "response": {
                      "outputSpeech": {
                        "ssml": "<speak> %(eventSummary)s kaaga Kurinji yai book seidhu vitaen </speak>" % locals(),
       
                        "type": "SSML"
                      },
                      "speechletResponse": {
                        "outputSpeech": {
                          "ssml": "<speak> Have booked Kurinji for %(eventSummary)s. </speak>" % locals(),
                        },
                        "shouldEndSession": False
                      }
                    },
                    "sessionAttributes": {}
                 }
    else:
       response = {
                    "version": "1.0",
                    "response": {
                      "outputSpeech": {
                        "ssml": "<speak> Kurinji available aga illai.</speak>" % locals(),
       
                        "type": "SSML"
                      },
                      "speechletResponse": {
                        "outputSpeech": {
                          "ssml": "<speak> Kurinji available aga illai.</speak>" % locals(),
                        },
                        "shouldEndSession": False
                      }
                    },
                    "sessionAttributes": {}
                 }
  else:
       response = {
                    "version": "1.0",
                    "response": {
                        "directives": [
                            {
                                "type": "Dialog.Delegate"
                            }
                        ],
                       "shouldEndSession": False
                    },
                 "sessionAttributes": {}
              } 
  logging.warning("Send response")
  logging.warning(response)
  logging.warning("Log group name:")
  logging.warning(context)
  return response

def getResourceAvailability(event):
    service = getService();
    attendee = 'thoughtworks.com_526f6f6d2d496e6469612d436f696d6261746f72652d4b7572696e6a69@resource.calendar.google.com'
    start_time = event['request']['intent']['slots']['Date']['value']+"T"+event['request']['intent']['slots']['StartTime']['value']+":00+05:30"
    end_time = event['request']['intent']['slots']['Date']['value']+"T"+event['request']['intent']['slots']['EndTime']['value']+":00+05:30"
    freebusyReq= {
             "timeMin": start_time,
             "timeMax": end_time,
             "items": [
               {
                 "id": attendee
               }
             ],
             "timeZone": "Asia/Calcutta"
            }
    eventsResult = service.freebusy().query(body=freebusyReq).execute()
    cal_dict = eventsResult[u'calendars']
    logging.warning("*********************************************")
    logging.warning(cal_dict)
    return len(cal_dict[u'thoughtworks.com_526f6f6d2d496e6469612d436f696d6261746f72652d4b7572696e6a69@resource.calendar.google.com'][u'busy'])==0
  
def getService():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    return service

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    s3_client = boto3.client('s3')
    s3_client.download_file('calendar-for-alexa', 'calendar-python-quickstart.json', '/tmp/calendar-python-quickstart.json')
    credential_path = '/tmp/calendar-python-quickstart.json'

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def createEvent(event):
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    service =getService()

    # if str(sys.argv[4])== 'Kurinji':
    location = 'Coimbatore-1F-Kurinji (4)'
    attendee = 'thoughtworks.com_526f6f6d2d496e6469612d436f696d6261746f72652d4b7572696e6a69@resource.calendar.google.com'
    # elif str(sys.argv[4])== 'Mullai':
    #   location = 'Coimbatore-1F-Mullai (4)'
    #   attendee = 'thoughtworks.com_526f6f6d2d496e6469612d436f696d6261746f72652d4d756c6c6169@resource.calendar.google.com'
    # else:
    #   location = ''
    #   attendee = ''

    calendarEvent = {
      'summary': event['request']['intent']['slots']['Summary']['value'],
      'location': location,
      'description': 'Event created by Alexa',
      'start': {
        'dateTime': event['request']['intent']['slots']['Date']['value']+"T"+event['request']['intent']['slots']['StartTime']['value']+":00+05:30"  },
      'end': {
        'dateTime': event['request']['intent']['slots']['Date']['value']+"T"+event['request']['intent']['slots']['EndTime']['value']+":00+05:30" },
      'attendees': [
        {'email': attendee}
      ]}
    eventResult = service.events().insert(calendarId='thoughtworks.com_m3nmis234ga2ad555lprcpgcvo@group.calendar.google.com', body=calendarEvent).execute()
    return eventResult
