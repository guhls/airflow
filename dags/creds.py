import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import json

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

dirname = os.path.dirname(__file__)
filename_credentials = os.path.join(dirname, 'credentials.json')
filename_token = os.path.join(dirname, 'token.json')

with open(filename_credentials, 'r') as credential_file:
    client_config = json.load(credential_file)


def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(filename_token):
        creds = Credentials.from_authorized_user_info(filename_token, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(filename_token, 'w') as token:
            token.write(creds.to_json())
    return creds