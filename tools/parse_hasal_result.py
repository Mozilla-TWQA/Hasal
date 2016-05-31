from __future__ import division
import os
import json
import argparse
from argparse import ArgumentDefaultsHelpFormatter


class HasalBugSubmitter(object):

    _BUG_SUMMARY = 'Firefox slower than {browser} {percent:.2%}({diff:.0f}ms) when {action}'
    _BUG_TEMPLATE = {
        'product': 'Core',
        'component': 'General',
        'version': '45 Branch',
        'rep_platform': 'x86_64',
        'op_sys': 'Linux',
        'blocks': ['1260981'],
        'summary': ''
    }

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
                        prepared_bugs.append(bug_data)
        # file the prepared bugs
        if len(prepared_bugs) > 0:
            submitted_bugs = []
            skipped_bugs = []
            # TODO: file bugs
            for bug in prepared_bugs:
                print('[Bug]: ' + json.dumps(bug, indent=4))
                yn = raw_input('>> Would you want to file the above bug? (y/n) ')
                if yn.lower().startswith('y'):
                    # TODO: file bug, then print return bug_id
                    print('Submitted. (not implemented)')
                    bug['id'] = 12345
                    submitted_bugs.append(bug)
                else:
                    print('SKIP.')
                    skipped_bugs.append(bug)

            # TODO: finally print all submitted/skipped bugs


def main():
    try:
        HasalBugSubmitter().cli().run()
    except Exception as e:
        print('[Error] {}'.format(e))
        exit(1)


if __name__ == '__main__':
    main()