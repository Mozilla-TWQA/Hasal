from __future__ import division
import os
import json
import argparse
from argparse import ArgumentDefaultsHelpFormatter
from bugzilla.agents import *
from bugzilla.utils import *


class BugAgent(BugzillaAgent):
    def __init__(self, username=None, password=None, api_key=None):
        super(BugAgent, self).__init__('https://bugzilla.mozilla.org/rest/', username, password, api_key)


class HasalBugSubmitter(object):

    _BUG_SUMMARY = 'Firefox slower than {browser} {percent:.2%}({diff:.0f}ms) when {action}'
    _BUG_TEMPLATE = {
        'product': 'Core',
        'component': 'General',
        'version': '45 Branch',
        'rep_platform': 'x86_64',
        'op_sys': 'Linux',
        'blocks': ['1260981'],
        'summary': '',
        'description': ''
    }
    _BUG_DESC_TEMPLATE = """
# Result
## Firefox
    - Median: {firefox_med_time:.0f} ms
    - Average: {firefox_avg_time:.0f} ms
    - Standard Deviation: {firefox_std_dev:.2f}
## Chrome
    - Median: {chrome_med_time:.0f} ms
    - Average: {chrome_avg_time:.0f} ms
    - Standard Deviation: {chrome_std_dev:.2f}
## Test Script
    - {firefox_test_script}
    - {chrome_test_script}
"""

    def __init__(self):
        self.input_json = None

    def cli(self):
        """
        Handle the argument parse, and the return the instance itself.
        """
        # argument parser
        arg_parser = argparse.ArgumentParser(description='Parse the result.json of Hasal, then submit the bugs.',
                                             formatter_class=ArgumentDefaultsHelpFormatter)
        arg_parser.add_argument('--input', action='store', dest='input_json', default=None,
                                help='Input result.json file.', required=True)
        # parse args and setup the logging
        args = arg_parser.parse_args()
        # assign variable
        input_json_file = os.path.join(os.getcwd(), args.input_json)
        if os.path.isfile(input_json_file):
            self.input_json = input_json_file
        else:
            raise Exception('{} is not a file.'.format(input_json_file))
        # return instance
        return self

    def get_tests_group_by_browser(self):
        ret_dict = {}
        input_dict = json.load(open(self.input_json))
        for item in input_dict:
            browser_name, test_name = item.replace('test_', '').split('_', 1)
            contents = {}
            for key in ['avg_time', 'std_dev', 'max_time', 'min_time', 'med_time']:
                contents[key] = input_dict[item][key]
            contents['test_script'] = item
            if test_name not in ret_dict:
                ret_dict[test_name] = {}
            ret_dict[test_name][browser_name] = contents
        return ret_dict

    def run(self):
        """
        Entry point.
        """
        tests_group_by_browser = self.get_tests_group_by_browser()
        prepared_bugs = []
        for test in tests_group_by_browser:
            if len(tests_group_by_browser[test]) >= 2:
                data_firefox = {}
                data_chrome = {}
                if 'firefox' in tests_group_by_browser[test]:
                    data_firefox = tests_group_by_browser[test]['firefox']
                if 'chrome' in tests_group_by_browser[test]:
                    data_chrome = tests_group_by_browser[test]['chrome']

                if data_firefox and data_chrome:
                    # if ff slower than others, prepare data for filing bug
                    bug_data = self._BUG_TEMPLATE.copy()
                    if data_firefox['med_time'] > data_chrome['med_time']:
                        med_time_diff_firefox_chrome = data_firefox['med_time'] - data_chrome['med_time']
                        med_time_percentage_firefox_chrome = med_time_diff_firefox_chrome / data_chrome['med_time']
                        bug_data['summary'] = self._BUG_SUMMARY.format(browser='Chrome',
                                                                       percent=med_time_percentage_firefox_chrome,
                                                                       diff=med_time_diff_firefox_chrome,
                                                                       action='running ' + test)
                        bug_data['description'] = self._BUG_DESC_TEMPLATE.format(firefox_med_time=data_firefox['med_time'],
                                                                                 firefox_avg_time=data_firefox['avg_time'],
                                                                                 firefox_std_dev=data_firefox['std_dev'],
                                                                                 firefox_test_script=data_firefox['test_script'],
                                                                                 chrome_med_time=data_chrome['med_time'],
                                                                                 chrome_avg_time=data_chrome['avg_time'],
                                                                                 chrome_std_dev=data_chrome['std_dev'],
                                                                                 chrome_test_script=data_chrome['test_script'])
                        prepared_bugs.append(bug_data)
        # file the prepared bugs
        count_prepared_bugs = len(prepared_bugs)
        count = 1
        if count_prepared_bugs > 0:
            submitted_bugs = []
            skipped_bugs = []
            failed_bugs = []
            # file bugs
            # We can use "None" for both instead to not authenticate
            username, password, api_key = get_credentials()
            # Load our agent for BMO
            bmo = BugAgent(username, password, api_key)
            for bug in prepared_bugs:
                print('[Bug {}/{}]\n{}'.format(count, count_prepared_bugs, json.dumps(bug, indent=4)))
                yn = raw_input('>> Would you want to file the above bug? (y/n) ')
                if yn.lower().startswith('y'):
                    try:
                        ret = bmo.create_bug(bug)
                        if 'id' in ret:
                            bug['id'] = ret['id']
                            print('Submitted. (not implemented)')
                            submitted_bugs.append(bug)
                        else:
                            print('[Error {}] {}'.format(ret['code'], ret['message']))
                            failed_bugs.append(bug)
                    except Exception as e:
                        print('[Error] {}'.format(e))
                        failed_bugs.append(bug)
                else:
                    print('SKIP.')
                    skipped_bugs.append(bug)

            # Remove Credentials
            remove_credentials()

            print('####################')
            print('[Submitted Bug List]')
            for bug in submitted_bugs:
                print('Bug {} - {}'.format(bug['id'], bug['summary']))
            print('\n[Skipped Bug List]')
            for bug in skipped_bugs:
                print('Skip - {}'.format(bug['summary']))
            print('\n[Failed Bug List]')
            for bug in failed_bugs:
                print('Fail - {}'.format(bug['summary']))


def main():
    try:
        HasalBugSubmitter().cli().run()
        print('')
    except Exception as e:
        print('[Error] {}'.format(e))
        exit(1)


if __name__ == '__main__':
    main()