# -*- coding: utf-8
import github3
import json
import os
from getpass import getpass

KEY_LABEL = 'iskakalunan'
STATE_SUCCESS = 'success'
STATE_PENDING = 'pending'


class githubHook(object):
    def __init__(self):
        user, password = self._get_credentials()
        g = github3.login(user, password)
        self.hasal = g.repository('Mozilla-TWQA', 'Hasal')

    def _get_credentials(self):
        github_credential = 'github.json'
        if os.path.isfile(github_credential):
            with open('github.json') as f:
                gh = json.load(f)
        else:
            gh = {}
            gh['user'] = raw_input("user: ").strip()
            gh['password'] = getpass()
            with open(github_credential, 'w') as f:
                json.dump(gh, f)
        return gh['user'], gh['password']

    def update_job_result_by_pr_number(self, pr_number, result):
        pr = self.hasal.pull_request(str(pr_number))
        self.hasal.create_status(pr.head.sha, result, context='iskakalunan')

    def get_requests(self):
        local_queue = []
        for pr in self.hasal.pull_requests():
            issue = pr.issue()
            if KEY_LABEL in [x.name for x in issue.original_labels]:
                status_list = [x.state for x in hasal.statuses(pr.head.sha)]
                state = '' if len(status_list) == 0 else status_list[0]
                if state == '':
                    hasal.crate_status(pr.head.sha, STATE_PENDING, context='iskakalunan')
                    local_queue.append(pr)
                elif state == STATE_PENDING:
                    local_queue.append(pr)
            else:
                self.hasal.create_status(pr.head.sha, STATE_SUCCESS, context='iskakalunan')
        return local_queue

    def checkout_pr(pr):
        os.system('git fetch origin')
        os.system('git checkout pr/' + str(pr.number))
