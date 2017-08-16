"""

Usage:
  backfill_agent.py [--query] [--latest] [-i=<str>]
  backfill_agent.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --query                   Query latest data.
  --latest                  Automatically check latest nightly build.
  -i=<str>                  Automatically refill data from json file.
"""

import os
import csv
import sys
import time
import json
import random
import platform
import datetime
import subprocess
from docopt import docopt


# common function
def call_subprocess(input_cmd):
    ret_code = subprocess.call(input_cmd, shell=True)
    if ret_code != 0:
        sys.exit(ret_code)


# predefine static data
BROWSER_SET = ['firefox', 'chrome']
MACHINE_SET = ['windows8-64', 'windows10-64']
PLATFORM_DICT = {'Windows-10': 'windows10-64', 'Windows-7': 'windows8-64'}
tmp_file = 'tmp.txt'
csv_file = 'tmp.csv'
backfill_json_template = os.path.join('tools', 'backfill_latest_template.json')
backfill_json_run = os.path.join('tools', 'backfill_latest_run.json')
backfill_python = os.path.join('tools', 'generate_data_for_nightly_build.py')

task_schedule = {
    "amazon_ail_hover_related_product_thumbnail Median": ["0500", "1700"],
    "amazon_ail_select_search_suggestion Median": ["0530", "1730"],
    "amazon_ail_type_in_search_field Median": ["0600", "1800"],
    "facebook_ail_click_close_chat_tab Median": ["0900", "2100"],
    "facebook_ail_click_open_chat_tab Median": ["0830", "2030"],
    "facebook_ail_click_open_chat_tab_emoji Median": ["0800", "2000"],
    "facebook_ail_click_photo_viewer_right_arrow Median": ["0930", "2130"],
    "facebook_ail_scroll_home_1_txt Median": ["1000", "2200"],
    "facebook_ail_type_comment_1_txt Median": ["1030", "2230"],
    "facebook_ail_type_composerbox_1_txt Median": ["1100", "2300"],
    "facebook_ail_type_message_1_txt Median": ["1130", "2330"],
    "gdoc_ail_pagedown_10_text Median": ["0430", "1630"],
    "gmail_ail_compose_new_mail_via_keyboard Median": ["0330", "1530"],
    "gmail_ail_open_mail Median": ["0200", "1400"],
    "gmail_ail_reply_mail Median": ["0300", "1500"],
    "gmail_ail_type_in_reply_field Median": ["0400", "1600"],
    "gsearch_ail_select_image_cat Median": ["0630", "1830"],
    "gsearch_ail_select_search_suggestion Median": ["0700", "1900"],
    "gsearch_ail_type_searchbox Median": ["0730", "1930"],
    "youtube_ail_select_search_suggestion Median": ["0000", "1200"],
    "youtube_ail_type_in_search_field Median": ["0100", "1300"]
}


def create_csv(query_days):
    # query data
    query_sec = query_days * 24 * 60 * 60
    print "Start querying data... might takes a while!"
    cmd = 'python tools/query_data_from_perfherder.py --interval={} > {}'.format(query_sec, tmp_file)
    call_subprocess(cmd)
    with open(tmp_file) as fin, open(csv_file, 'w') as fout:
        o = csv.writer(fout)
        o.writerow(['suite_name', '_', 'browser_type', 'machine_platform', 'date', 'time', 'value'])
        for line in fin:
            o.writerow(line.split())
    print "Done query data!"
    os.remove(tmp_file)


def run_backfill():
    # clean space, remove output_config
    call_subprocess('del /F/S/Q output_config')

    # run generate data
    call_subprocess('python {} -i {}'.format(backfill_python, backfill_json_run))


class BFagent(object):
    def __init__(self):
        self.backfill_list = []
        self.history_dates = []
        # reference date is the day we aim to check for
        # Here we set the reference date one day before local time (Taiwan)
        self.ref_date = (datetime.date.today() -
                         datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # predefine data structure
        self.dot_count = dict()
        for b in BROWSER_SET:
            self.dot_count[b] = {}
            for s in task_schedule.keys():
                self.dot_count[b][s] = 0

        # check current platform
        self.current_platform = ''
        for p in PLATFORM_DICT.keys():
            if p in platform.platform():
                self.current_platform = PLATFORM_DICT[p]

    def reset_date_list_dict(self):
        # Reset the reference date, back fill task list, and counter
        self.backfill_list = []
        self.ref_date = (datetime.date.today() -
                         datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # Counter must be set to 0 for next round
        for b in BROWSER_SET:
            for s in task_schedule.keys():
                self.dot_count[b][s] = 0

    def analyze_csv(self):
        with open(csv_file) as f:
            r = csv.DictReader(f)
            for row in r:
                _s = '{} {}'.format(row['suite_name'], row['_'])
                _m = row['machine_platform']
                _b = row['browser_type']
                _d = row['date']

                if row['suite_name'] == 'suite_name':
                    continue
                elif _m != self.current_platform or _b not in BROWSER_SET:
                    continue
                elif self.ref_date != _d:
                    continue
                else:
                    self.dot_count[_b][_s] += 1
        os.remove(csv_file)

    def list_recover_data(self):
        # check if need to recover
        # TODO: assign different goal by time

        # Every day must have 6 points
        ref_count = 6
        for s in task_schedule.keys():
            for b in BROWSER_SET:
                __count = self.dot_count[b][s]
                missing = ref_count - __count
                if missing > 0:
                    self.backfill_list.append([b, s, missing])
                    print 'Missing', b, s, missing

    def create_json(self, refill_date='latest'):
        # create json file for running
        with open(backfill_json_template) as fin, open(backfill_json_run, 'w') as fout:
            for line in fin:
                if '\"ADD_FIREFOX_BUILD_PATH\"' in line:
                    # The input here determines how many time should each case runs.
                    # Here, we only run each case once for every run
                    if refill_date == 'latest':
                        fout.write('\"latest-mozilla-central/\"')
                    else:
                        fout.write('\"{}\"'.format(refill_date))

                elif '\"TEMPLATE\": \"ADD_SUITE_HERE\"' in line:
                    # always random select 5 cases to run
                    case_count = 5
                    if case_count < len(self.backfill_list):
                        ran_select = random.sample(self.backfill_list, case_count)
                    else:
                        ran_select = self.backfill_list

                    i = 0
                    for task in ran_select:
                        i += 1
                        suite = task[1].split()[0]
                        app = task[1].split()[0].split('_')[0]
                        _b = task[0]
                        output_row = '\"{}\": {{\"case_list":[\"tests.regression.{}.test_{}_{}\"],' \
                                     '\"perfherder-suitename\": \"{}\"}}'.format(suite, app, _b, suite, suite)
                        fout.write(output_row)
                        if i != len(ran_select):
                            # add comma except the last row
                            fout.write(',')
                else:
                    # just copy other lines from template
                    fout.write(line)

    def run(self, need_query):
        """ Refill latest Nightly """
        if need_query or not os.path.isfile(csv_file):
            create_csv(2)  # just query last two dates data
        self.reset_date_list_dict()
        self.analyze_csv()
        self.list_recover_data()
        if len(self.backfill_list) == 0:
            print 'Congratulation! Everything was fine recently.'
        else:
            print 'Oops! Something is missing. I will help you recover it!'
            self.create_json()
            run_backfill()

    def run_history(self, backfill_config):
        # load date config file
        with open(backfill_config) as fh:
            self.history_dates = json.load(fh)
        self.history_dates = sorted(self.history_dates, reverse=True)

        # check all input are valid
        # TODO: add file checker

        # Request perherder counts for k days
        create_csv(len(self.history_dates))

        self.reset_date_list_dict()

        # random pick N days to back filled
        rand_num = 1
        if rand_num < len(self.history_dates):
            rand_dates = random.sample(self.history_dates, rand_num)
        else:
            rand_dates = self.history_dates

        # loop through all the dates pickeds
        for nightly_build_link in rand_dates:
            date = nightly_build_link[8:18]
            # set ref_date to config file
            print "\n=======================\n" \
                  "* Checking {} *\n" \
                  "=======================".format(date)
            self.reset_date_list_dict()
            self.ref_date = date
            self.analyze_csv()
            self.list_recover_data()
            if len(self.backfill_list) == 0:
                print 'Congratulation! Everything was fine on {}.'.format(self.ref_date)
            else:
                print 'Oops! Something is missing on {}.'.format(self.ref_date)
                print 'I will help you recover it!'
                self.create_json(nightly_build_link)
                run_backfill()


def wait_for_minutes(rest_minutes):
    division = 3
    print "Time to sleep"
    interval = rest_minutes / division
    for i in range(division):
        print "{} mins left...".format(rest_minutes - i * interval)
        time.sleep(60 * interval)


def main():
    arguments = docopt(__doc__)
    agent = BFagent()

    # run in different mode
    if arguments['--latest']:
        print "===============\n* Latest mode *\n==============="
        while True:
            agent.run(True)
            wait_for_minutes(3)
    elif arguments['-i']:
        print "================\n* History mode *\n================"
        while True:
            agent.run_history(arguments['-i'])
            wait_for_minutes(3)
    else:
        print "===============\n* Single mode *\n==============="
        agent.run(arguments['--query'])


if __name__ == '__main__':
    main()
