from __future__ import print_function
import base64
import email
from apiclient import errors
import httplib2
from apiclient import discovery
import re
import auth


SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail Test'

authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.get_credentials()

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)


def getMessageBody(msg_id):
    try:
        message = service.users().messages().get(userId="me", id=msg_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('utf-8'))
        msg_str = re.sub(r'=20.\n', '', msg_str)
        msg_str = re.sub(r'=.\n', '', msg_str)
        msg_str = re.sub(r'=20', '', msg_str)
        # print(msg_str)
        mime_msg = email.message_from_string(msg_str)
        print(mime_msg)
        messageMainType = mime_msg.get_content_maintype()

        if messageMainType == 'multipart':
            for part in mime_msg.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
            return ""
        elif messageMainType == 'text':
            return mime_msg.get_payload()
    except errors.HttpError, error:
        print("An error occurred: %s" % error)

# print(getMessageBody("1628b20e39967e44"))
getMessageBody("16295249bbb4f311")

str = """
Dear Students,=20

This=20is to confirm that the presentations will start tomorrow from 10:00 =
to
13:00 room 3.566.=20

Note:=20that the presentations are not open to the rest of the class.=20

Therefore,=20it is recommended that each group waits in front of the room (=
or
in the open space area) approximately 5 minutes the schedules time.=20

Please=20have your computer ready (if possible with a HDMI connection) and
have a copy of your presentation on a flash drive, in case you cannot
connect your computer to the AV system.

Please keep your presentations within the 10 minutes allocated to you.

Regards,=20

Didier
"""
