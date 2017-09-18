"""

Usage:
  query_data_from_perfherder.py [--query-signatures] [--interval=<str>] [--keyword=<str>] [--browser-type=<str>] [--platform=<str>] [--suite-name=<str>] [--begin-date=<str>] [--end-date=<str>] [--csv=<filename>]
  query_data_from_perfherder.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --query-signatures        Query signatures
  --interval=<str>          Query interval default is last 14 days [default: 1209600]
  --keyword=<str>           Query by app name [default: all]
  --browser-type=<str>      Query by browser type [default: all]
  --platform=<str>          Query by platform [default: all]
  --suite-name=<str>        Query by suite name [default: all]
  --begin-date=<str>        Query by begin date [default: all]
  --end-date=<str>          Query by end date [default: all]
  --csv=<filename>          Output to CSV file
"""

from __future__ import print_function

import os
import csv
import sys
import json
import copy
import time
import urllib2
from docopt import docopt
from datetime import datetime

DEFAULT_QUERY_OPTION = "all"
DEFAULT_HASAL_SIGNATURES = "hasal_perfherder_signatures.json"
DEFAULT_HASAL_FRAMEWORK_NO = 9
DEFAULT_PERFHERDER_PRODUCTION_URL = "https://treeherder.mozilla.org"
DEFAULT_PERFHERDER_STAGE_URL = "https://treeherder.allizom.org"
PROJECT_NAME_MOZILLA_CENTRAL = "mozilla-central"
API_URL_QUERY_SIGNATURE_LIST = "%s/api/project/%s/performance/signatures/?format=json&framework=%s"
API_URL_QUERY_DATA = "%s/api/project/%s/performance/data/?format=json&framework=%s&interval=%s&signatures=%s"


class QueryData(object):

    def send_url_data(self, url_str):
        DEFAULT_URL_HEADER = {'User-Agent': "Hasal Query Perfherder Tool"}
        request_obj = urllib2.Request(url_str, headers=DEFAULT_URL_HEADER)
        try:
            response_obj = urllib2.urlopen(request_obj)
        except Exception as e:
            print("Send post data failed, error message [%s]" % e.message)
            return None
        if response_obj.getcode() == 200:
            return response_obj
        else:
            print("response status code is [%d]" % response_obj.getcode())
            return None

    def query_signatures(self):
        url_str = API_URL_QUERY_SIGNATURE_LIST % (DEFAULT_PERFHERDER_PRODUCTION_URL, PROJECT_NAME_MOZILLA_CENTRAL, str(DEFAULT_HASAL_FRAMEWORK_NO))
        return_result = {'signature_data': {}, 'suite_list': [], 'browser_type_list': [], 'machine_platform_list': []}
        json_obj = None
        query_obj = self.send_url_data(url_str)
        if query_obj:
            json_obj = json.loads(query_obj.read())
        if json_obj:
            for revision in json_obj.keys():
                if 'test' not in json_obj[revision] and 'parent_signature' not in json_obj[revision] and 'has_subtests' in json_obj[revision]:
                    suite_name = json_obj[revision]['suite'].strip()
                    browser_type = json_obj[revision]['extra_options'][0].strip()
                    machine_platform = json_obj[revision]['machine_platform'].strip()
                    return_result['signature_data'][revision] = {'suite_name': suite_name,
                                                                 'browser_type': browser_type,
                                                                 'machine_platform': machine_platform}
                    if suite_name not in return_result['suite_list']:
                        return_result['suite_list'].append(suite_name)
                    if browser_type not in return_result['browser_type_list']:
                        return_result['browser_type_list'].append(browser_type)
                    if machine_platform not in return_result['machine_platform_list']:
                        return_result['machine_platform_list'].append(machine_platform)
            with open(DEFAULT_HASAL_SIGNATURES, "w+") as fh:
                json.dump(return_result, fh)
        return return_result

    def get_signature_list(self, signature_data, input_keyword, input_btype, input_platform, input_suite_name):

        if input_btype != DEFAULT_QUERY_OPTION:
            btype_sig_list = [sig for sig, data in signature_data['signature_data'].items() if
                              data.get('browser_type').lower() == input_btype]
            if len(btype_sig_list) == 0:
                print("The current input browser type [%s] is not in support list [%s]" % (input_btype, signature_data['browser_type_list']))
                return None
        else:
            btype_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        if input_platform != DEFAULT_QUERY_OPTION:
            platform_sig_list = [sig for sig, data in signature_data['signature_data'].items() if
                                 data.get('machine_platform').lower() == input_platform]
            if len(platform_sig_list) == 0:
                print("The current input platform [%s] is not in support list [%s]" % (input_platform, signature_data['machine_platform_list']))
                return None
        else:
            platform_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        if input_suite_name != DEFAULT_QUERY_OPTION:
            suite_sig_list = [sig for sig, data in signature_data['signature_data'].items() if
                              data.get('suite_name').lower() == input_suite_name]
            if len(suite_sig_list) == 0:
                print("The current input suite [%s] is not in support list [%s]" % (input_suite_name, signature_data['suite_list']))
                return None
        else:
            suite_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        if input_keyword != DEFAULT_QUERY_OPTION:
            suite_list = [suite_name.lower() for suite_name in signature_data['suite_list'] if input_keyword in suite_name.lower()]
            keyword_sig_list = [sig for sig, data in signature_data['signature_data'].items() if data.get('suite_name').lower() in suite_list]
        else:
            keyword_sig_list = copy.deepcopy(signature_data['signature_data'].keys())

        return list(set(btype_sig_list) & set(platform_sig_list) & set(suite_sig_list) & set(keyword_sig_list))

    def print_data(self, input_json, signature_data, b_date, e_date):
        b_timestamp = 0.0
        e_timestamp = 0.0
        try:
            if b_date != DEFAULT_QUERY_OPTION:
                b_date_obj = datetime.strptime(b_date, '%Y-%m-%d')
                b_timestamp = time.mktime(b_date_obj.timetuple())
            if e_date != DEFAULT_QUERY_OPTION:
                e_date_obj = datetime.strptime(e_date, '%Y-%m-%d')
                e_timestamp = time.mktime(e_date_obj.timetuple())
        except ValueError:
            print("Incorrect data format, should be YYYY-MM-DD!!, the begin_date and end_date filter will be ignored!")

        for sig in input_json:
            for data in input_json[sig]:
                if b_timestamp != 0.0:
                    if e_timestamp != 0.0:
                        if b_timestamp <= data['push_timestamp'] <= e_timestamp:
                            print('{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                                signature_data['signature_data'][sig]['suite_name'],
                                signature_data['signature_data'][sig]['browser_type'],
                                signature_data['signature_data'][sig]['machine_platform'],
                                datetime.utcfromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                                data['value']))
                    else:
                        if b_timestamp <= data['push_timestamp']:
                            print('{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                                signature_data['signature_data'][sig]['suite_name'],
                                signature_data['signature_data'][sig]['browser_type'],
                                signature_data['signature_data'][sig]['machine_platform'],
                                datetime.utcfromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                                data['value']))
                else:
                    if e_timestamp != 0.0:
                        if data['push_timestamp'] <= e_timestamp:
                            print('{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                                signature_data['signature_data'][sig]['suite_name'],
                                signature_data['signature_data'][sig]['browser_type'],
                                signature_data['signature_data'][sig]['machine_platform'],
                                datetime.utcfromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                                data['value']))
                    else:
                        print('{:50s} {:10s} {:20s} {:30s}  {:20f}'.format(
                            signature_data['signature_data'][sig]['suite_name'],
                            signature_data['signature_data'][sig]['browser_type'],
                            signature_data['signature_data'][sig]['machine_platform'],
                            datetime.utcfromtimestamp(data['push_timestamp']).strftime("%Y-%m-%d %H-%M-%S-%f"),
                            data['value']))

    def output_csv(self, input_json, signature_data, b_date, e_date, csv_writer):
        try:
            b_timestamp = 0.0
            e_timestamp = 0.0
            try:
                if b_date != DEFAULT_QUERY_OPTION:
                    b_date_obj = datetime.strptime(b_date, '%Y-%m-%d')
                    b_timestamp = time.mktime(b_date_obj.timetuple())
                if e_date != DEFAULT_QUERY_OPTION:
                    e_date_obj = datetime.strptime(e_date, '%Y-%m-%d')
                    e_timestamp = time.mktime(e_date_obj.timetuple())
            except ValueError:
                print(
                    "Incorrect data format, should be YYYY-MM-DD!!, the begin_date and end_date filter will be ignored!")

            for sig in input_json:
                for data in input_json[sig]:
                    if b_timestamp != 0.0:
                        if e_timestamp != 0.0:
                            if b_timestamp <= data['push_timestamp'] <= e_timestamp:
                                suite_name_full = signature_data['signature_data'][sig]['suite_name'].split()
                                suite_name = suite_name_full[0]
                                suite_name_type = suite_name_full[1]
                                data_date = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%Y-%m-%d')
                                data_time = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%H-%M-%S-%f')
                                csv_writer.writerow([suite_name,
                                                     suite_name_type,
                                                     signature_data['signature_data'][sig]['browser_type'],
                                                     signature_data['signature_data'][sig]['machine_platform'],
                                                     data_date,
                                                     data_time,
                                                     data['value']])
                        else:
                            if b_timestamp <= data['push_timestamp']:
                                suite_name_full = signature_data['signature_data'][sig]['suite_name'].split()
                                suite_name = suite_name_full[0]
                                suite_name_type = suite_name_full[1]
                                data_date = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%Y-%m-%d')
                                data_time = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%H-%M-%S-%f')
                                csv_writer.writerow([suite_name,
                                                     suite_name_type,
                                                     signature_data['signature_data'][sig]['browser_type'],
                                                     signature_data['signature_data'][sig]['machine_platform'],
                                                     data_date,
                                                     data_time,
                                                     data['value']])
                    else:
                        if e_timestamp != 0.0:
                            if data['push_timestamp'] <= e_timestamp:
                                suite_name_full = signature_data['signature_data'][sig]['suite_name'].split()
                                suite_name = suite_name_full[0]
                                suite_name_type = suite_name_full[1]
                                data_date = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%Y-%m-%d')
                                data_time = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%H-%M-%S-%f')
                                csv_writer.writerow([suite_name,
                                                     suite_name_type,
                                                     signature_data['signature_data'][sig]['browser_type'],
                                                     signature_data['signature_data'][sig]['machine_platform'],
                                                     data_date,
                                                     data_time,
                                                     data['value']])
                        else:
                            suite_name_full = signature_data['signature_data'][sig]['suite_name'].split()
                            suite_name = suite_name_full[0]
                            suite_name_type = suite_name_full[1]
                            data_date = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%Y-%m-%d')
                            data_time = datetime.utcfromtimestamp(data['push_timestamp']).strftime('%H-%M-%S-%f')
                            csv_writer.writerow([suite_name,
                                                 suite_name_type,
                                                 signature_data['signature_data'][sig]['browser_type'],
                                                 signature_data['signature_data'][sig]['machine_platform'],
                                                 data_date,
                                                 data_time,
                                                 data['value']])
        except Exception as e:
            print(e)

    def query_data(self, query_interval, query_keyword, query_btype, query_platform, query_suite_name, query_begin_date, query_end_date, csv_filename=None):
        if not os.path.exists(DEFAULT_HASAL_SIGNATURES):
            signature_data = self.query_signatures()
        else:
            with open(DEFAULT_HASAL_SIGNATURES) as fh:
                signature_data = json.load(fh)

        signature_list = self.get_signature_list(signature_data, query_keyword.lower().strip(),
                                                 query_btype.lower().strip(), query_platform.lower().strip(),
                                                 query_suite_name.lower().strip())

        csv_writer = None
        if csv_filename:
            if not csv_filename.endswith('.csv'):
                csv_filename = '{}.csv'.format(csv_filename)
            print('Starting output to {} ...'.format(csv_filename))
            csv_fh = open(csv_filename, 'w')
            csv_writer = csv.writer(csv_fh)
            csv_writer.writerow(['suite_name', '_', 'browser_type', 'machine_platform', 'date', 'time', 'value'])

        for signature in signature_list:
            url_str = API_URL_QUERY_DATA % (DEFAULT_PERFHERDER_PRODUCTION_URL, PROJECT_NAME_MOZILLA_CENTRAL, str(DEFAULT_HASAL_FRAMEWORK_NO), str(query_interval), signature)
            query_obj = self.send_url_data(url_str)
            if query_obj:
                json_obj = json.loads(query_obj.read())
                if csv_filename:
                    print('.', end='')
                    sys.stdout.flush()
                    self.output_csv(json_obj, signature_data, query_begin_date.strip(), query_end_date.strip(),
                                    csv_writer)
                else:
                    self.print_data(json_obj, signature_data, query_begin_date.strip(), query_end_date.strip())

        if csv_filename:
            print('\nOutput to {} done.'.format(csv_filename))


def main():

    arguments = docopt(__doc__)
    query_data_obj = QueryData()
    if arguments['--query-signatures']:
        query_data_obj.query_signatures()
    else:
        query_data_obj.query_data(query_interval=arguments['--interval'], query_keyword=arguments['--keyword'],
                                  query_btype=arguments['--browser-type'], query_platform=arguments['--platform'],
                                  query_suite_name=arguments['--suite-name'],
                                  query_begin_date=arguments['--begin-date'], query_end_date=arguments['--end-date'],
                                  csv_filename=arguments['--csv'])

if __name__ == '__main__':
    main()
