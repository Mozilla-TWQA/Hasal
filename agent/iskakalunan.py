# -*- coding: utf-8

import mailTask
import githubHook
import subprocess
import logging
import json
import os
from hasalTask import HasalTask

logger = logging.getLogger('iskakalunan')
logging.basicConfig(format='%(module)s %(levelname)s %(message)s', level=logging.DEBUG)

ISKAKALUNAN_NOTE = 'iskakalunan.note'


class Iskakalunan(object):
    def __init__(self, name="iskakalunan", **kwargs):
        self.name = name
        self.kwargs = kwargs
        logging.info("Check mail credential")
        self.mail_handler = mailTask.MailTask()
        logging.info("Check github hooker credential")
        self.github_handler = githubHook.githubHook()
        if self.github_handler is None:
            logging.warning("Github authorization failed")

    def run(self):
        # Check if there's in-progress job
        if os.path.isfile(ISKAKALUNAN_NOTE):
            with open(ISKAKALUNAN_NOTE, 'r') as f:
                note = json.load(f)
            # if job is finished
            if note['type'] == 'mailTask':
                if not self.mail_handler.check_job_status():
                    return
                else:
                    self.mail_handler.update_job_results()
            elif note['type'] == 'githubHook':
                # TODO: add result checker
                if not os.path.isfile('result.json'):
                    self.github_handler.update_job_result_by_pr_number(note['pr_number'], 'failure', 'no-result')
                else:
                    with open('result.json', 'r') as f:
                        result = json.load(f)
                    if 'test_firefox_gdoc_read_basic_txt_1' in result \
                            and 'total_time' in result['test_firefox_gdoc_read_basic_txt_1'] \
                            and result['test_firefox_gdoc_read_basic_txt_1']['total_time'] > 0:
                        self.github_handler.update_job_result_by_pr_number(note['pr_number'], 'success', 'success')
                    else:
                        self.github_handler.update_job_result_by_pr_number(note['pr_number'], 'failure', 'no-result')
            if 'pr_number' in note:
                subprocess.call(['git', 'checkout', 'dev'])
                subprocess.call(['git', 'branch', '-D', 'pr/' + str(note['pr_number'])])
            try:
                os.remove(ISKAKALUNAN_NOTE)
                os.remove('result.json')
            except Exception as e:
                print(e)
            return

        # reset environment
        note = {}
        subprocess.call(['git', 'checkout', 'dev'])

        # is there any new CI request
        pull_requests = self.github_handler.get_requests()
        logging.info('{} pull requests with iskakalunan tag'.format(len(pull_requests)))
        if pull_requests:
            note['type'] = 'githubHook'
            note['pr_number'] = pull_requests[0].number
            note['sha'] = pull_requests[0].head.sha
            note['status'] = 'pending'
            # TODO: add a function to install the newest nightly
            with open(ISKAKALUNAN_NOTE, 'w') as f:
                json.dump(note, f)
            self.github_handler.checkout_pr(pull_requests[0])
            # execute
            self.kwargs['MAX_RUN'] = 1
            self.kwargs['MAX_RETRY'] = 1
            self.kwargs['INDEX_CONFIG_NAME'] = 'runtimeDctGenerator.json'
            hasal = HasalTask(name="iskakalunan_task", **self.kwargs)
            cmd_list = hasal.generate_command_list()
            print(' '.join(cmd_list))
            try:
                subprocess.call(cmd_list, env=os.environ.copy())
            except Exception as e:
                print e.message
            return

        # is there any new Mail request
        messages = self.mail_handler.get_requests()
        if messages:
            note['type'] = 'mailTask'
            self.mail_handler.execute_job(messages[0])
            return

    def handle_mail_task(self):
        # HANDLE MAIL AGENT #
        mail_task = mailTask.MailTask()

        # NewRequest to InQueue
        messages = mail_task.fetch_messages(mail_task.LABEL_NEW_REQUEST)
        logger.info("Check New Requests: %d request(s) get" % len(messages))

        for message in messages:
            if message.validation:
                update_body = {"removeLabelIds": [mail_task.LABEL_NEW_REQUEST],
                               "addLabelIds": [mail_task.LABEL_IN_QUEUE]}
                mail_task.updateLabels(message, update_body)
            else:
                update_body = {"removeLabelIds": [mail_task.LABEL_NEW_REQUEST],
                               "addLabelIds": [mail_task.LABEL_REPLIED]}
                mail_task.updateLabels(message, update_body)
                mail_task.reply_status(message, mail_task.MSG_TYPE_INVALID_REQUEST)

        # Check if InProcess exists
        msg_in_process = mail_task.fetch_messages(mail_task.LABEL_IN_PROCESS)
        logger.info("Check In Process job exists: %d Job(s) on machine" % len(msg_in_process))

        # Check if in process job is finished
        job_empty = False
        if msg_in_process and mail_task.check_job_status():
            update_body = {"removeLabelIds": [mail_task.LABEL_IN_PROCESS],
                           "addLabelIds": [mail_task.LABEL_REPLIED]}
            mail_task.update_labels(msg_in_process[0], update_body)
            mail_task.reply_status(msg_in_process[0], mail_task.MSG_TYPE_JOB_FINISHED)
            job_empty = True
        elif not msg_in_process:
            job_empty = True
        if job_empty:
            messages = mail_task.fetch_messages(mail_task.LABEL_IN_QUEUE)
            logger.info("Check In Queue tasks: %d tasks in queue" % len(messages))

            # start to execute new job
            if messages:
                update_body = {"removeLabelIds": [mail_task.LABEL_IN_QUEUE],
                               "addLabelIds": [mail_task.LABEL_IN_PROCESS]}
                mail_task.update_labels(messages[0], update_body)
                mail_task.reply_status(messages[0], mail_task.MSG_TYPE_UNDER_EXECUTION)
                mail_task.prepare_job(messages[0])

if __name__ == '__main__':
    iskakalunan = Iskakalunan()
    iskakalunan.run()
    print("Job done")
