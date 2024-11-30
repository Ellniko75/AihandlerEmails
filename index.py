import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from Email import Email
from aiHandler import extractInfo
from google.auth.exceptions import RefreshError
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as error:
                print("!!!!!!!!!!!! TOKEN NEEDS REFRESHING!!!!!!!")
                os.remove("./token.json")
                return main()

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me", q=f"newer_than:4d").execute()
        # Get all the emails
        email_array = getMails(results, service)
        # We extract the important data with the AI model
        for email in email_array:
            info = extractInfo(email)
            print(email.__dict__)
            # print(info.__dict__)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def getMails(results, service):
    email_array = []

    for message in results.get('messages', []):
        msg_id = message['id']
        message_details = service.users().messages().get(userId='me', id=msg_id).execute()
        message = message_details['payload']

        # Variables to fill with data
        msg_id_data = msg_id
        from_message = ""
        message_data = ""

        for header in message['headers']:
            if header['name'] == 'From':
                from_message = header['value']
                break

        if 'parts' in message:
            parts = message['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    message_body = part['body']['data']
                    data_raw = str(base64.urlsafe_b64decode(
                        message_body).decode('utf-8'))

                    data_parsed = data_raw.replace('\n', ' ').replace('\r', '')

                    # Create Email Object and add to array
                    email_object = Email(
                        msg_id_data=msg_id_data, message_data=data_parsed, from_message=from_message)

                    email_array.append(email_object)
                    break

    return email_array


if __name__ == "__main__":
    main()
