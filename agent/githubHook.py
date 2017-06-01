# -*- coding: utf-8
import github3
import os
from getpass import getpass

KEY_LABEL = 'iskakalunan'
STATE_SUCCESS = 'success'
STATE_PENDING = 'pending'


class githubHook(object):
    def __init__(self):
        g = self._get_credentials()
        if g is None:
            return None
        self.hasal = g.repository('Mozilla-TWQA', 'Hasal')

    def _get_credentials(self):
        github_credential = 'github.json'
        if os.path.isfile(github_credential):
            with open('github.json', 'r') as f:
                token = f.readline().strip()
            return github3.login(token=token)
        else:
            return None

    def update_job_result_by_pr_number(self, pr_number, result):
        pr = self.hasal.pull_request(str(pr_number))
        self.hasal.create_status(pr.head.sha, result, context='iskakalunan')

    def get_requests(self):
        local_queue = []
        for pr in self.hasal.pull_requests():
            issue = pr.issue()
            if KEY_LABEL in [x.name for x in issue.original_labels]:
                status_list = [x.state for x in self.hasal.statuses(pr.head.sha)]
                state = '' if len(status_list) == 0 else status_list[0]
                if state == '':
                    self.hasal.crate_status(pr.head.sha, STATE_PENDING, context='iskakalunan')
                    local_queue.append(pr)
                elif state == STATE_PENDING:
                    local_queue.append(pr)
        return local_queue

    def checkout_pr(pr):
        os.system('git fetch origin')
        os.system('git checkout pr/' + str(pr.number))

if __name__ == '__main__':
    if not os.path.isfile('github.json'):
        try:
            user = raw_input('User Account for Github: ').strip()
            password = getpass('Password: ').strip()
            scopes = ['user', 'repo']
            note = 'Iskakalunan'
            note_url = 'https://github.com/Mozilla-TWQA/Hasal'
            auth = github3.authorize(user, password, scopes, note, note_url)
            with open('github.json', 'w'):
                f.write(auth.token + '\r\n')
                f.write(str(auth.id))
        except Exception as e:
            print e
