# coding=utf-8
from __future__ import print_function
from oauth2client import tools
import base64
import email
from apiclient import errors
import re

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class gmail:

    def __init__(self, service, user_id, label_ids=[]):
        self.service = service
        self.user_id = user_id
        self.label_ids = label_ids


    def get_labels(self, service):
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name']+ " "+label['id'])


    def message_numbers_in_a_label(self):
        message = self.service.users().labels().get(id=self.label_ids[0], userId=self.user_id).execute()
        if not message:
            return 0
        else:
            return message["messagesTotal"]


    def listMessagesWithLabels(self):
          try:
            response = self.service.users().messages().list(userId=self.user_id, labelIds=self.label_ids[0]).execute()
            messages = []
            if 'messages' in response:
              messages.extend(response['messages'])

            while 'nextPageToken' in response:
              page_token = response['nextPageToken']
              response = self.service.users().messages().list(userId=self.user_id,
                                                         labelIds=self.label_ids[0],
                                                         pageToken=page_token).execute()
              messages.extend(response['messages'])

            return messages
          except errors.HttpError, error:
            print('An error occurred: %s' % error)


    def getMessageBody(self, msg_id):
        try:
            message = self.service.users().messages().get(userId=self.user_id, id=msg_id, format='raw').execute()
            msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            msg_str = re.sub(r'=20.\n', ' ', msg_str)
            msg_str = re.sub(r'=.\n', ' ', msg_str)
            msg_str = re.sub(r'=20', ' ', msg_str)
            mime_msg = email.message_from_string(msg_str)
            messageMainType = mime_msg.get_content_maintype()

            if messageMainType == 'multipart':
                for part in mime_msg.get_payload():
                    if part.get_content_maintype() == 'text':
                        return part.get_payload().split('CONFIDENTIALITY NOTICE')[0]
                return ""
            elif messageMainType == 'text':
                return mime_msg.get_payload().split('CONFIDENTIALITY NOTICE')[0]
        except errors.HttpError, error:
                print("An error occurred: %s" % error)

# .split('CONFIDENTIALITY NOTICE')[0]