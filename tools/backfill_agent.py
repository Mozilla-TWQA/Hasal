"""

Usage:
  backfill_agent.py [--query] [--latest] [-i=<str>] [--debug]
  backfill_agent.py [--backfill] [--debug] [<days>]
  backfill_agent.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --query                   Query latest data.
  --latest                  Automatically check latest nightly build.
  -i=<str>                  Automatically refill data from json file.
  --backfill                Automatically backfill previous <days> days (include current day). Default days is 0, only current day.
  --debug                   Debug Mode [default: False]
"""

import os
import re
import csv
import json
import time
import random
import shutil
import logging
import platform
import datetime
import urlparse
import requests
from dateutil import tz
from docopt import docopt

from query_data_from_perfherder import QueryData
from generate_data_for_nightly_build import GenerateData


# predefine static data
ARCHIVE_NIGHTLY_SERVER = 'http://archive.mozilla.org/pub/firefox/nightly/'

BROWSER_SET = ['firefox', 'chrome']
MACHINE_SET = ['windows8-64', 'windows10-64']
PLATFORM_DICT = {'Windows-10': 'windows10-64', 'Windows-7': 'windows8-64'}
csv_file = 'backfill.csv'
backfill_json_template = os.path.join('tools', 'backfill_latest_template.json')
backfill_json_run = os.path.join('tools', 'backfill_latest_run.json')
from_zone = tz.tzutc()
to_zone = tz.tzlocal()

task_schedule = [
    "amazon_ail_hover_related_product_thumbnail Median",
    "amazon_ail_select_search_suggestion Median",
    "amazon_ail_type_in_search_field Median",
    "facebook_ail_click_close_chat_tab Median",
    "facebook_ail_click_open_chat_tab Median",
    "facebook_ail_click_open_chat_tab_emoji Median",
    "facebook_ail_click_photo_viewer_right_arrow Median",
    "facebook_ail_scroll_home_1_txt Median",
    "facebook_ail_type_comment_1_txt Median",
    "facebook_ail_type_composerbox_1_txt Median",
    "facebook_ail_type_message_1_txt Median",
    "gdoc_ail_pagedown_10_text Median",
    "gmail_ail_compose_new_mail_via_keyboard Median",
    "gmail_ail_open_mail Median",
    "gmail_ail_reply_mail Median",
    "gmail_ail_type_in_reply_field Median",
    "gsearch_ail_select_image_cat Median",
    "gsearch_ail_select_search_suggestion Median",
    "gsearch_ail_type_searchbox Median",
    "youtube_ail_select_search_suggestion Median",
    "youtube_ail_type_in_search_field Median"
]


def create_csv(query_days):
    """
    query data.
    @param query_days:
    @return: True if query and create successfully.
    """
    DEFAULT_QUERY_OPTION = "all"
    query_sec = query_days * 24 * 60 * 60
    print "Start querying data... might takes a while!"

    query_data_obj = QueryData()
    try:
        query_data_obj.query_data(query_interval=str(query_sec),
                                  query_keyword=DEFAULT_QUERY_OPTION,
                                  query_btype=DEFAULT_QUERY_OPTION,
                                  query_platform=DEFAULT_QUERY_OPTION,
                                  query_suite_name=DEFAULT_QUERY_OPTION,
                                  query_begin_date=DEFAULT_QUERY_OPTION,
                                  query_end_date=DEFAULT_QUERY_OPTION,
                                  csv_filename=csv_file)
    except Exception as e:
        logging.error(e)
        return False

    print "Done query data!"
    return True


def run_backfill():
    # clean space, remove output_config
    dest = 'output_config'
    shutil.rmtree(dest, ignore_errors=True)

    # run generate data
    generate_data_obj = GenerateData(backfill_json_run)
    generate_data_obj.trigger()


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
            for s in task_schedule:
                self.dot_count[b][s] = 0

        # check current platform
        self.current_platform = ''
        for p in PLATFORM_DICT.keys():
            if p in platform.platform():
                self.current_platform = PLATFORM_DICT[p]

        print('Current Platform: {}'.format(self.current_platform))

    def reset_date_list_dict(self):
        # Reset the reference date, back fill task list, and counter
        self.backfill_list = []
        self.ref_date = (datetime.date.today() -
                         datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # Counter must be set to 0 for next round
        for b in BROWSER_SET:
            for s in task_schedule:
                self.dot_count[b][s] = 0

    def find_ref_date_from_csv_for_latest(self):
        """
        Default ref_date is previous day, if there is any today result in CSV, then change ref_date to today.
        @return:
        """
        _ref_datetime = datetime.datetime.strptime(self.ref_date, '%Y-%m-%d')

        with open(csv_file) as f:
            r = csv.DictReader(f)
            for row in r:
                _d = row['date']

                # find the latest date in query result (default ref_date is previous day)
                _input_datetime = datetime.datetime.strptime(_d, '%Y-%m-%d')
                if _input_datetime > _ref_datetime:
                    self.ref_date = _d
        print('Set Reference Date after analyze CSV: {}'.format(self.ref_date))
        return self.ref_date

    def analyze_csv(self, latest=True):

        if latest:
            self.find_ref_date_from_csv_for_latest()

        with open(csv_file) as f:
            r = csv.DictReader(f)
            for row in r:
                _s = '{} {}'.format(row['suite_name'], row['_'])
                _m = row['machine_platform']
                _b = row['browser_type']
                _d = row['date']
                # _t = '{} {}'.format(row['date'], row['time'])

                if _s not in task_schedule:
                    continue
                elif _m != self.current_platform or _b not in BROWSER_SET:
                    continue

                if self.ref_date != _d:
                    continue
                else:
                    self.dot_count[_b][_s] += 1

    def list_recover_data(self):
        # There must be at least 6 points each day
        target_count = 6
        for case in task_schedule:
            for browser in BROWSER_SET:
                case_value_count = self.dot_count[browser][case]
                missing = max((target_count - case_value_count), 0)
                if missing > 0:
                    self.backfill_list.append([browser, case, missing])
                    print('Missing {browser} {case} ... {missing} ({count}/{target})'.format(browser=browser,
                                                                                             case=case,
                                                                                             missing=missing,
                                                                                             count=case_value_count,
                                                                                             target=target_count))

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
                    # In latest mode, random select 5 cases to run.
                    # In history mode, run all suite
                    max_suite_num = 5
                    if refill_date == 'latest' and len(self.backfill_list) > max_suite_num:
                        selected_suites = random.sample(self.backfill_list, max_suite_num)
                    else:
                        selected_suites = self.backfill_list

                    i = 0
                    for task in selected_suites:
                        i += 1
                        suite = task[1].split()[0]
                        app = task[1].split()[0].split('_')[0]
                        _b = task[0]
                        output_row = '\"{}\": {{\"case_list":[\"tests.regression.{}.test_{}_{}\"],' \
                                     '\"perfherder-suitename\": \"{}\"}}'.format(suite, app, _b, suite, suite)
                        fout.write(output_row)
                        if i != len(selected_suites):
                            # add comma except the last row
                            fout.write(',')
                else:
                    # just copy other lines from template
                    fout.write(line)

    def run(self, need_query):
        """ Refill latest Nightly """
        if need_query or not os.path.isfile(csv_file):
            # just query last two dates data
            ret = create_csv(2)
            if not ret:
                return False

        self.reset_date_list_dict()
        self.analyze_csv(latest=True)
        self.list_recover_data()
        if len(self.backfill_list) == 0:
            print 'Congratulation! Everything was fine recently.'
        else:
            print 'Oops! Something is missing. I will help you recover it!'
            self.create_json()
            run_backfill()

        # Remove csv file when this round finished
        os.remove(csv_file)
        return True

    def run_history(self, backfill_config):
        # load date config file
        with open(backfill_config) as fh:
            self.history_dates = json.load(fh)
        self.history_dates = sorted(self.history_dates, reverse=True)

        # check all input are valid
        # TODO: add file checker

        # Assume back fill dates are in 14 days
        ret = create_csv(14)
        if not ret:
            return False

        # loop through all the dates picked
        for nightly_build_link in self.history_dates:
            date = nightly_build_link[8:18]
            # set ref_date to config file
            print "\n=======================\n" \
                  "* Checking {} *\n" \
                  "=======================".format(date)
            self.reset_date_list_dict()
            self.ref_date = date
            self.analyze_csv(latest=False)
            print('Set Reference Date: {}'.format(self.ref_date))

            self.list_recover_data()
            if len(self.backfill_list) == 0:
                print 'Congratulation! Everything was fine on {}.'.format(self.ref_date)
            else:
                print 'Oops! Something is missing on {}.'.format(self.ref_date)
                print 'I will help you recover it!'
                self.create_json(nightly_build_link)
                run_backfill()

        # Remove csv file when this round finished
        os.remove(csv_file)
        return True

    @staticmethod
    def get_url_data(url):
        timeout_min = 2
        for _ in range(10):
            try:
                response = requests.get(url, timeout=timeout_min * 60)
                return response
            except Exception as e:
                logging.error(e)
        raise Exception('Can not get data from {}'.format(url))

    @staticmethod
    def get_build_url_data_base_on_current_date(build_date_str=None):
        """
        Get build URL list from Archive server base on today.
        @return: dict obj. ex: {'2017-09-20-22-04-31': '2017/09/2017-09-20-22-04-31-mozilla-central/', ...}
        """
        if build_date_str is None:
            build_date_str = datetime.date.today().strftime('%Y-%m-%d')
        year_str, month_str, day_str = build_date_str.split('-')

        base_url = urlparse.urljoin(ARCHIVE_NIGHTLY_SERVER, '{}/'.format(year_str))
        base_url = urlparse.urljoin(base_url, '{}/'.format(month_str))

        ret_dict = {}
        logging.info('Accessing URL: {}'.format(base_url))
        try:
            response = BFagent.get_url_data(base_url)
            if response.status_code == 200:
                html = response.text
                pattern = r'href="([\w/\-_]+-mozilla-central/)"'
                url_list = re.findall(pattern, html)

                # build_url example: /pub/firefox/nightly/2017/09/2017-09-01-10-03-09-mozilla-central/
                for build_url in url_list:
                    # build_folder example: 2017-09-01-10-03-09-mozilla-central
                    _, build_folder, _ = build_url.rsplit('/', 2)
                    # build_date_time example: 2017-09-01-10-03-09
                    build_date_time, _, _ = build_folder.rsplit('-', 2)

                    # build_sub_url example: 2017/09/2017-09-01-10-03-09-mozilla-central/
                    _, _, _, _, build_sub_url = build_url.split('/', 4)

                    ret_dict[build_date_time] = build_sub_url
        except Exception as e:
            logging.error(e)
        return ret_dict

    @staticmethod
    def generate_previous_days_list(build_date_str, days_count=14):
        """
        Generate days list which contains current build date.
        @param build_date_str: string, "YYYY-MM-DD". ex: "2017-09-20".
        @param days_count: how many days. max is 30. ex: 14.
        @return: list, ex: ['2017-09-20', '2017-09-19', '2017-09-18', ...]
        """
        latest_build_date_obj = datetime.datetime.strptime(build_date_str, '%Y-%m-%d')

        days_count = min(days_count, 30)

        ret_list = [build_date_str]
        for idx in range(1, days_count + 1):
            previous_date = (latest_build_date_obj - datetime.timedelta(days=idx)).strftime("%Y-%m-%d")
            logging.debug('previous {} day is {}'.format(idx, previous_date))
            ret_list.append(previous_date)
        return ret_list

    def run_backfill(self, days_str):
        """

        @param days_str:
        @return: True if has missing value.
        """
        if days_str is None:
            backfile_days = 0
            logging.info('Backfill only current day.'.format(backfile_days))
        else:
            days_int = int(days_str)
            if days_int <= 0:
                backfile_days = 0
                logging.info('Backfill only current day.'.format(backfile_days))
            else:
                backfile_days = min(days_int, 30)
                logging.info('Backfill {} days.'.format(backfile_days))

        ret = create_csv(backfile_days + 1)
        if not ret:
            return False

        build_urls_dict = self.get_build_url_data_base_on_current_date()

        latest_build_date = None
        for build_datetime, build_sub_url in build_urls_dict.items():
            if latest_build_date is None:
                latest_build_date = build_datetime[0:10]
            elif latest_build_date < build_datetime:
                latest_build_date = build_datetime[0:10]
        if latest_build_date is None:
            return False
        logging.info('Get Latest Build Date: {}'.format(latest_build_date))
        previous_days = self.generate_previous_days_list(latest_build_date, days_count=backfile_days)

        logging.info('Previous {} Days: {}'.format(backfile_days, previous_days))

        previous_days_build_url_list = []
        for day in previous_days:
            matched_build_datetime = [build_datetime for build_datetime in build_urls_dict.keys() if day in build_datetime]
            if matched_build_datetime:
                previous_days_build_datetime = sorted(matched_build_datetime)[0]
                previous_days_build_url_list.append(build_urls_dict.get(previous_days_build_datetime))
            else:
                # miss match, might be previous month, retry once
                build_urls_dict.update(self.get_build_url_data_base_on_current_date(build_date_str=day))

                matched_build_datetime = [build_datetime for build_datetime in build_urls_dict.keys() if day in build_datetime]
                if matched_build_datetime:
                    previous_days_build_datetime = sorted(matched_build_datetime)[-1]
                    previous_days_build_url_list.append(build_urls_dict.get(previous_days_build_datetime))

        logging.info('Checking following builds:\n  {}'.format(previous_days_build_url_list))

        # loop through all the dates picked
        has_missing_value = False
        for build_url in previous_days_build_url_list:
            build_date = build_url[8:18]

            print('\n=======================\n* Checking {} *\n======================='.format(build_date))
            self.reset_date_list_dict()
            self.ref_date = build_date
            self.analyze_csv(latest=False)
            print('Set Reference Date: {}'.format(self.ref_date))

            self.list_recover_data()
            if len(self.backfill_list) == 0:
                print('Congratulation! Everything was fine recently.')
            else:
                print('Oops! Something is missing. I will help you recover it!')
                has_missing_value = True
                self.create_json(build_url)
                run_backfill()

        # Remove csv file when this round finished
        os.remove(csv_file)
        return has_missing_value


def main():
    arguments = docopt(__doc__)

    default_log_format = '%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s'
    default_datefmt = '%Y-%m-%d %H:%M'
    if arguments['--debug']:
        logging.basicConfig(level=logging.DEBUG, format=default_log_format, datefmt=default_datefmt)
    else:
        logging.basicConfig(level=logging.INFO, format=default_log_format, datefmt=default_datefmt)

    agent = BFagent()

    sleep_hour = 1
    # run in different mode
    if arguments['--latest']:
        print('===============\n* Latest mode *\n===============')
        while True:
            run_flag = agent.run(True)
            # sleep and wait for next time if all builds is okay
            if not run_flag:
                logging.info('Sleep {} hour and wait for next run...'.format(sleep_hour))
                time.sleep(sleep_hour * 60 * 60)
    elif arguments['--backfill']:
        print('================\n* Backfill mode *\n================')
        while True:
            run_flag = agent.run_backfill(arguments['<days>'])
            # sleep and wait for next time if all builds is okay
            if not run_flag:
                logging.info('Sleep {} hour and wait for next run...'.format(sleep_hour))
                time.sleep(sleep_hour * 60 * 60)
    elif arguments['-i']:
        print('================\n* History mode *\n================')
        while True:
            run_flag = agent.run_history(arguments['-i'])
            # sleep and wait for next time if all builds is okay
            if not run_flag:
                logging.info('Sleep {} hour and wait for next run...'.format(sleep_hour))
                time.sleep(sleep_hour * 60 * 60)
    else:
        print('===============\n* Single mode *\n===============')
        agent.run(arguments['--query'])


if __name__ == '__main__':
    main()
