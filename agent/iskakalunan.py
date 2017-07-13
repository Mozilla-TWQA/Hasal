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
                if not os.path.isfile('result.json'):
                    self.mail_handler.reply_status(status='This is a notifier that your request is failed in execution')
                else:
                    self.mail_handler.reply_status(status='This is a notifier that your request is finished.')
            elif note['type'] == 'githubHook':
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
            with open(ISKAKALUNAN_NOTE, 'w') as f:
                json.dump(note, f)
            self.mail_handler.execute_job(messages[0])
            return

if __name__ == '__main__':
    iskakalunan = Iskakalunan()
    iskakalunan.run()
    print("Job done")
