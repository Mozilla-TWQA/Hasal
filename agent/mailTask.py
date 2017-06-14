# -*- coding: utf-8

from __future__ import print_function
import httplib2
import urllib2
import requests
import os
import re
import base64
import subprocess
import shutil
import zipfile
import mimetypes
import logging
import argparse
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from apiclient import discovery, errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from hasalTask import HasalTask

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Iskakalunan'

LABEL_NEW_REQUEST = 'Label_8'
LABEL_IN_QUEUE = 'Label_4'
LABEL_IN_PROCESS = 'Label_5'
LABEL_REPLIED = 'Label_6'

RESULT_ZIP = 'result.zip'
RESULT_JSON = 'result.json'
UPLOAD_FOLDER = 'upload'
FIREFOX_PATH = r'C:/Program Files/Mozilla Firefox'

MSG_TYPE_INVALID_REQUEST = 'This is a notifier that your request is invalid.'
MSG_TYPE_UNDER_EXECUTION = 'This is a notifier that your request is under execution.'
MSG_TYPE_JOB_FINISHED = 'This is a notifier that your request is finished.'

logger = logging.getLogger('mailTask')
logging.basicConfig(format='%(module)s %(levelname)s %(message)s', level=logging.DEBUG)


class MailTask(object):
    def __init__(self, name="mailTask", **kwargs):
        """Basic Iskakalunan model

        messages: mail queue on g-mail
        """
        self.name = name
        self.credentials = self.get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)
        self.kwargs = kwargs

    def run(self):
        """Runner for Hasal agent
        """
        # NewRequest to InQueue
        messages = self.fetch_messages(LABEL_NEW_REQUEST)
        logger.info("Check New Requests: %d request(s) get" % len(messages))

        for message in messages:
            if message.validation:
                update_body = {"removeLabelIds": [LABEL_NEW_REQUEST],
                               "addLabelIds": [LABEL_IN_QUEUE]}
                self.update_labels(message, update_body)
            else:
                update_body = {"removeLabelIds": [LABEL_NEW_REQUEST],
                               "addLabelIds": [LABEL_REPLIED]}
                self.update_labels(message, update_body)
                self.reply_status(message, MSG_TYPE_INVALID_REQUEST)

        # Check if InProcess exists
        msg_in_process = self.fetch_messages(LABEL_IN_PROCESS)
        logger.info("Check In Process job exists: %d Job(s) on machine" % len(msg_in_process))

        # Check if in process job is finished
        job_empty = False
        if msg_in_process and self.check_job_status():
            update_body = {"removeLabelIds": [LABEL_IN_PROCESS],
                           "addLabelIds": [LABEL_REPLIED]}
            self.update_labels(msg_in_process[0], update_body)
            self.reply_status(msg_in_process[0], MSG_TYPE_JOB_FINISHED)
            job_empty = True
        elif not msg_in_process:
            job_empty = True
        if job_empty:
            messages = self.fetch_messages(LABEL_IN_QUEUE)
            logger.info("Check In Queue tasks: %d tasks in queue" % len(messages))
            if messages:
                update_body = {"removeLabelIds": [LABEL_IN_QUEUE],
                               "addLabelIds": [LABEL_IN_PROCESS]}
                self.update_labels(messages[0], update_body)
                self.reply_status(messages[0], MSG_TYPE_UNDER_EXECUTION)
                self.prepare_job(messages[0])

    def execute_job(self, message):
        update_body = {"removeLabelIds": [LABEL_IN_QUEUE],
                       "addLabelIds": [LABEL_IN_PROCESS]}
        self.update_labels(message, update_body)
        self.reply_status(message, MSG_TYPE_UNDER_EXECUTION)
        self.prepare_job(message)

    def get_requests(self):
        messages = self.fetch_messages(LABEL_NEW_REQUEST)
        logger.info("Check New Requests: %d request(s) get" % len(messages))

        for message in messages:
            if message.validation:
                update_body = {"removeLabelIds": [LABEL_NEW_REQUEST],
                               "addLabelIds": [LABEL_IN_QUEUE]}
                self.update_labels(message, update_body)
            else:
                update_body = {"removeLabelIds": [LABEL_NEW_REQUEST],
                               "addLabelIds": [LABEL_REPLIED]}
                self.update_labels(message, update_body)
                self.reply_status(message, MSG_TYPE_INVALID_REQUEST)
        messages = self.fetch_messages(LABEL_IN_QUEUE)
        logger.info("Check In Queue tasks: %d tasks in queue" % len(messages))
        return messages

    def update_job_results(self):
        msg = self.fetch_messages(LABEL_IN_PROCESS)
        update_body = {"removeLabelIds": [LABEL_IN_PROCESS],
                       "addLabelIds": [LABEL_REPLIED]}
        self.update_labels(msg, update_body)
        self.reply_status(msg, MSG_TYPE_JOB_FINISHED)

    def fetch_messages(self, label_id):
        """Fetch messages from pre-set mail account

        valid results will be updated to messages
            - Valid result means messages contain 'Iskakalunan' (case insensitive)
            - Only messages tags w/ 'NewRequest', 'InQueue', and 'InProcess'
        """
        try:
            response = self.service.users().messages().list(userId='me', labelIds=label_id).execute()
            message_list = []
            messages = []
            if 'messages' in response:
                message_list.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId=user_id,
                                                           labelIds=label_id,
                                                           pageToken=page_token).execute()
                message_list.extend(response['messages'])

            for message in message_list:
                message_content = self.service.users().messages().get(userId='me', id=message['id']).execute()
                message_temp = Message(message['id'], message['threadId'], message_content)
                if 'moztpeqa' not in message_temp.sender:
                    logger.debug("message sender: %s" % message_temp.sender)
                    messages.append(message_temp)

            return messages
        except errors.HttpError, error:
            logger.error("An error occurred: %s" % error)

    def update_labels(self, msg, labels):
        try:
            logger.debug('Update labels for msgId: %s with %s' % (msg.message_id, labels))
            self.service.users().messages().modify(userId='me', id=msg.message_id, body=labels).execute()
        except errors.HttpError, error:
            logger.error('An error occurred: %s' % error)

    def prepare_try_build(self, revision):
        try:
            url_try_builds = "https://archive.mozilla.org/pub/firefox/try-builds/"
            req = urllib2.Request(url_try_builds)
            response = urllib2.urlopen(req)
            html_try_builds = response.read()

            pattern = 'href="(.+' + revision + '\/)"'
            m = re.search(pattern, html_try_builds)
            url_revision_build = "https://archive.mozilla.org" + m.group(1) + "try-win64/firefox-55.0a1.en-US.win64.zip"
            logger.debug("Download build from %s" % url_revision_build)
            r = requests.get(url_revision_build, stream=True)
            with open('firefox.zip', 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    f.write(chunk)

            with zipfile.ZipFile('firefox.zip', 'r') as zf:
                zf.extractall()
            shutil.rmtree(FIREFOX_PATH)
            shutil.move('firefox', FIREFOX_PATH)
        except Exception as e:
            logger.error("Failed to grab builds for testing: %s" % e)

    def prepare_job(self, msg):
        """Prepare a json represent a job and update message status
        """
        self.prepare_try_build(msg.revision)

        self.kwargs['INDEX_CONFIG_NAME'] = 'runtimeDctGenerator.json'
        hasal = HasalTask(name="iskakalunan_task", **self.kwargs)
        cmd_list = hasal.generate_command_list()
        logger.debug("cmd: %s" % ' '.join(cmd_list))

        try:
            subprocess.call(cmd_list, env=os.environ.copy)
        except Exception as e:
            print(e.message)

    def check_job_status(self):
        """Check if a job is finished

        return - True if a job is finished
        """
        if os.path.isdir(UPLOAD_FOLDER) and os.path.isfile(os.path.join(UPLOAD_FOLDER, max(os.listdir(UPLOAD_FOLDER)), RESULT_JSON)):
            if os.path.isfile(RESULT_ZIP):
                os.remove(RESULT_ZIP)
            shutil.make_archive("result", 'zip', os.path.join(UPLOAD_FOLDER, max(os.listdir(UPLOAD_FOLDER))))
            logger.info("Job finished by checking")
            return True
        else:
            logger.info("Job did not finish by checking")
            return False

    def reply_status(self, msg, status):
        """Update status to sender"""
        logger.debug("reply status to %s with %s" % (msg.message_id, status))
        message = MIMEMultipart()
        message['From'] = 'moztpeqa@mozilla.com'
        message['To'] = msg.sender
        message['Subject'] = msg.subject
        text = MIMEText(status)
        message.attach(text)

        if status == MSG_TYPE_JOB_FINISHED:
            path = os.path.join(os.getcwd(), RESULT_ZIP)
            content_type, encoding = mimetypes.guess_type(path)

            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            with open(path, 'rb') as fp:
                message_attachment = MIMEBase(main_type, sub_type)
                message_attachment.set_payload(fp.read())

                message_attachment.add_header('Content-Disposition', 'attachment', filename=RESULT_ZIP)
                message.attach(message_attachment)

        raw_message = {'raw': base64.urlsafe_b64encode(message.as_string())}
        raw_message['threadId'] = msg.thread_id
        self.service.users().messages().send(userId='me', body=raw_message).execute()

    def get_credentials(self):
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
        credential_path = os.path.join(credential_dir,
                                       'iskakalunan.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            logger.debug("no credential exists, request to authentication")
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            credentials = tools.run_flow(flow, store, flags)
            logger.info('Storing credentials to ' + credential_path)
        return credentials


class Message(object):
    def __init__(self, message_id, thread_id, contents):
        """Basic Message Type
        message_id: unique message ID
        thread_id: thread ID for easier find a message

        status: status handled by Iskakalunan
        parameters: parameters requested in a message
        """
        self.message_id = message_id
        self.thread_id = thread_id
        self.sender, self.subject = self.__resolve_headers(contents)
        self.body = self.__resolve_body(contents)

        self.revision = ""
        self.test_suite = ""
        self.calc_si = ""
        self.advance = ""
        self.max_run = "30"
        self.max_retry = "15"

        self.validation = self.__isValid()
        self.getInfo()

    def getInfo(self):
        logger.debug("self.revision: %s" % self.revision)
        logger.debug("self.test_suite: %s" % self.test_suite)
        logger.debug("self.calc_si: %s" % self.calc_si)
        logger.debug("self.advance: %s" % self.advance)
        logger.debug("self.max_run: %s" % self.max_run)
        logger.debug("self.max_retry: %s" % self.max_retry)

    def __resolve_headers(self, contents):
        subject = ""
        sender = ""
        for x in contents['payload']['headers']:
            if x['name'] == 'From':
                sender = x['value']
            if x['name'] == 'Subject':
                subject = x['value']
        return sender, subject

    def __resolve_body(self, contents):
        if 'body' in contents['payload'] and contents['payload']['body']['size'] > 0:
            return contents['payload']['body']['data']
        elif 'parts' in contents['payload'] and contents['payload']['parts'][0]['body']['size'] > 0:
            return contents['payload']['parts'][0]['body']['data']
        else:
            return ""

    def __isValid(self):
        msg_body = base64.urlsafe_b64decode(self.body.encode('utf-8')).split('\r\n')

        isLink = False
        for line in msg_body:
            line = line.replace('\xe2\x80\x8b', '')
            if isLink:
                self.revision = line[-40:]
                isLink = False
            elif line.startswith("Build"):
                if len(line) < 60:
                    isLink = True
                    logger.debug("commit is a link")
                else:
                    self.revision = line[-40:]
            elif line.startswith("Suite:"):
                self.test_suite = ''.join(line[6:].split())
                with open('test.suite', 'w') as f:
                    f.write(self.test_suite)
            elif line.endswith("--calc_si"):
                self.calc_si = "--calc_si"
            elif line.startswith("Advance:") and "yes" == line[9:].lower():
                self.advance = "--advance"
            elif line.startswith("--max-run="):
                self.max_run = line[10:]
            elif line.startswith("--max-retry="):
                self.max_retry = line[12:]

        if len(self.revision) < 40:
            logger.warning("revision is too short: %s" % self.revision)
            return False
        if not self.max_run.isdigit() and not self.max_retry.isdigit():
            logger.warning("max_run and max_retry must be numbers")
            return False
        return True


if __name__ == '__main__':
    iskakalunan = MailTask()

    # NewRequest to InQueue
    messages = iskakalunan.fetch_messages(LABEL_NEW_REQUEST)
    logger.info("Check New Requests: %d request(s) get" % len(messages))

    for message in messages:
        if message.validation:
            update_body = {"removeLabelIds": [LABEL_NEW_REQUEST],
                           "addLabelIds": [LABEL_IN_QUEUE]}
            iskakalunan.update_labels(message, update_body)
        else:
            update_body = {"removeLabelIds": [LABEL_NEW_REQUEST],
                           "addLabelIds": [LABEL_REPLIED]}
            iskakalunan.update_labels(message, update_body)
            iskakalunan.reply_status(message, MSG_TYPE_INVALID_REQUEST)

    # Check if InProcess exists
    msg_in_process = iskakalunan.fetch_messages(LABEL_IN_PROCESS)
    logger.info("Check In Process job exists: %d Job(s) on machine" % len(msg_in_process))

    # Check if in process job is finished
    job_empty = False
    if msg_in_process and iskakalunan.check_job_status():
        update_body = {"removeLabelIds": [LABEL_IN_PROCESS],
                       "addLabelIds": [LABEL_REPLIED]}
        iskakalunan.update_labels(msg_in_process[0], update_body)
        iskakalunan.reply_status(msg_in_process[0], MSG_TYPE_JOB_FINISHED)
        job_empty = True
    elif not msg_in_process:
        job_empty = True
    if job_empty:
        messages = iskakalunan.fetch_messages(LABEL_IN_QUEUE)
        logger.info("Check In Queue tasks: %d tasks in queue" % len(messages))
        if messages:
            update_body = {"removeLabelIds": [LABEL_IN_QUEUE],
                           "addLabelIds": [LABEL_IN_PROCESS]}
            iskakalunan.update_labels(messages[0], update_body)
            iskakalunan.reply_status(messages[0], MSG_TYPE_UNDER_EXECUTION)
            iskakalunan.prepare_job(messages[0])
