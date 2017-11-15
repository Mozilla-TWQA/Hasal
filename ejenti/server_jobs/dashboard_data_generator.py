import copy
import json
import logging
from datetime import datetime
from numpy import median

from lib.common.gistUtil import GISTUtil
from lib.helper.generateBackfillTableHelper import GenerateBackfillTableHelper


class DashboardDataGenerator(object):
    PLATFORM = 'win64'

    KEY_PERFHERDER_DATA = 'perfherder_data'
    KEY_VLAUE = 'value'

    KEY_TIMESTAMP = 'timestamp'
    KEY_TIMESTAMP_JS = 'timestamp_js'
    KEY_CASENAME = 'casename'
    KEY_BROWSER = 'browser'
    KEY_PLATFORM = 'platform'
    KEY_VALUE_LIST = 'value_list'
    KEY_REVISON = 'revision'
    KEY_SIGNATURE = 'signature'

    BROWSER_FIREFOX = 'firefox'
    BROWSER_CHROME = 'chrome'
    BROWSER_FIREFOX_MEDIAN = 'firefox_median'
    BROWSER_CHROME_MEDIAN = 'chrome_median'

    PLATFORM_WIN7 = 'windows8-64'
    PLATFORM_WIN10 = 'windows10-64'

    RESULT_AMOUNT = 6
    KEY_OVERALL_TOTAL_CASE_NUMBER = 'total_case_number'
    KEY_OVERALL_FINISH_CASE_NUMBER = 'finish_case_number'
    KEY_OVERALL_FINISH_PERCENTAGE = 'finish_percentage'
    KEY_OVERALL_GAUGE = 'gauge'
    KEY_OVERALL_CASES = 'cases'
    KEY_OVERALL_SUITE_STATUS = 'suite_status'

    COLOR_FIREFOX = 'rgba(232, 163, 23, 1)'
    COLOR_FIREFOX_OPACITY = 'rgba(232, 163, 23, 0.3)'
    SYMBOL_FIREFOX = 'circle'

    COLOR_CHROME = 'rgba(189, 21, 80, 1)'
    COLOR_CHROME_OPACITY = 'rgba(189, 21, 80, 0.3)'
    SYMBOL_CHROME = 'triangle'

    JS_DATA_TEMPLATE = {
        'chart': {
            'type': 'spline'
        },
        'title': {
            'text': ''
        },
        'xAxis': {
            'type': 'datetime',
            'dateTimeLabelFormats': {
                'month': '%e. %b',
                'year': '%b'
            },
            'title': {
                'text': 'Date'
            }
        },
        'yAxis': {
            'title': {
                'text': 'Asynchronize Input latency (ms)'
            },
            'min': 0
        },
        'tooltip': {
            'headerFormat': '<b>{series.name}</b><br>',
            'pointFormat': '{point.x:%e. %b, %H:%M} - {point.y:.2f} ms'
        },
        'plotOptions': {
            'spline': {
                'marker': {
                    'enabled': True
                }
            }
        },
        'series': []
    }

    JS_DATA_SERIES_OBJ_TEMPLATE = {
        'name': '',
        'type': 'scatter',
        'data': []
    }

    JS_DATA_SERIES_MEDIAN_OBJ_TEMPLATE = {
        'name': '',
        'data': []
    }

    JS_GAUGE_TEMPLATE = {
        'chart': {
            'type': 'solidgauge',
            'backgroundColor': '#1a1a1a'
        },
        'title': None,
        'pane': {
            'center': ['50%', '100%'],
            'size': '200%',
            'startAngle': -90,
            'endAngle': 90,
            'background': {
                'backgroundColor': '#1a1a1a',
                'innerRadius': '60%',
                'outerRadius': '100%',
                'shape': 'arc'
            }
        },
        'tooltip': {
            'enabled': False
        },
        'yAxis': {
            'stops': [
                [0.1, '#ff0000'],
                [0.5, '#ffff00'],
                [0.9, '#00ff00']
            ],
            'lineWidth': 0,
            'minorTickInterval': None,
            'tickAmount': 0,
            'tickPixelInterval': 0,
            'labels': {
                'enabled': False
            },
            'min': 0,
            'max': 100,
            'tickInterval': 0.01,
            'tickWidth': 0
        },
        'plotOptions': {
            'solidgauge': {
                'dataLabels': {
                    'y': 5,
                    'borderWidth': 0,
                    'useHTML': True
                }
            }
        },
        'credits': {
            'enabled': False
        },
        'series': []
    }

    JS_GAUGE_SERIES_OBJ_TEMPLATE = {
        'name': '',
        'data': [],
        'dataLabels': {
            'format': '<div style="text-align:center"><span style="font-size:25px;color:silver">{y}%</span></div>',
        },
        'tooltip': {
            'valueSuffix': ''
        }
    }

    def __init__(self):
        self.source_data = []
        self.casename_set = set()
        self.latest_timestamp = ''
        self.latest_28_builds_timestamp_list = []

        self._generate_source_data()

    def _generate_source_data(self):
        table_obj = GenerateBackfillTableHelper.get_history_archive_perfherder_relational_table(
            DashboardDataGenerator.PLATFORM)

        ret_list = []

        if table_obj:
            self.latest_timestamp = sorted(table_obj.keys())[-1]
            self.latest_timestamp_js = int(self.latest_timestamp) * 1000
            # get 28 builds (almost 14 days) timestamp
            self.latest_28_builds_timestamp_list = sorted(table_obj.keys())[-28:]

            for timestamp in self.latest_28_builds_timestamp_list:
                revison = table_obj.get(timestamp, {}).get(DashboardDataGenerator.KEY_REVISON, '')
                perf_data_obj_dict = table_obj.get(timestamp, {}).get(DashboardDataGenerator.KEY_PERFHERDER_DATA, {})

                for key, value in perf_data_obj_dict.items():
                    ret_obj = {}

                    # ex: amazon_ail_type_in_search_field:firefox:windows8-64
                    casename, browser, platform = key.split(':')

                    self.casename_set.add(casename)

                    value_list = value.get(DashboardDataGenerator.KEY_VLAUE)
                    signature = value.get(DashboardDataGenerator.KEY_SIGNATURE)

                    ret_obj[DashboardDataGenerator.KEY_TIMESTAMP] = timestamp
                    ret_obj[DashboardDataGenerator.KEY_TIMESTAMP_JS] = int(timestamp) * 1000
                    ret_obj[DashboardDataGenerator.KEY_CASENAME] = casename
                    ret_obj[DashboardDataGenerator.KEY_BROWSER] = browser
                    ret_obj[DashboardDataGenerator.KEY_PLATFORM] = platform
                    ret_obj[DashboardDataGenerator.KEY_VALUE_LIST] = value_list
                    ret_obj[DashboardDataGenerator.KEY_SIGNATURE] = signature
                    ret_obj[DashboardDataGenerator.KEY_REVISON] = revison

                    ret_list.append(ret_obj)

            # traverse all timestamp to check all "casename:browser:platform" has value list.
            for timestamp in self.latest_28_builds_timestamp_list:
                revison = table_obj.get(timestamp, {}).get(DashboardDataGenerator.KEY_REVISON, '')
                for casename in self.casename_set:
                    for browser in [DashboardDataGenerator.BROWSER_FIREFOX, DashboardDataGenerator.BROWSER_CHROME]:
                        for platform in [DashboardDataGenerator.PLATFORM_WIN7, DashboardDataGenerator.PLATFORM_WIN10]:
                            ret = [obj for obj in ret_list if
                                   obj.get(DashboardDataGenerator.KEY_TIMESTAMP) == timestamp and
                                   obj.get(DashboardDataGenerator.KEY_CASENAME) == casename and
                                   obj.get(DashboardDataGenerator.KEY_BROWSER) == browser and
                                   obj.get(DashboardDataGenerator.KEY_PLATFORM) == platform]
                            if not ret:
                                logging.debug('Timestamp {ts} missed {c}:{b}:{p} value list, added an empty list.'.format(ts=timestamp, c=casename, b=browser, p=platform))
                                no_value_obj = {
                                    DashboardDataGenerator.KEY_TIMESTAMP: timestamp,
                                    DashboardDataGenerator.KEY_TIMESTAMP_JS: int(timestamp) * 1000,
                                    DashboardDataGenerator.KEY_CASENAME: casename,
                                    DashboardDataGenerator.KEY_BROWSER: browser,
                                    DashboardDataGenerator.KEY_PLATFORM: platform,
                                    DashboardDataGenerator.KEY_VALUE_LIST: [],
                                    DashboardDataGenerator.KEY_SIGNATURE: '',
                                    DashboardDataGenerator.KEY_REVISON: revison
                                }
                                ret_list.append(no_value_obj)

        self.source_data = ret_list
        return ret_list

    def generate_data_for_platform(self, platform):
        """

        @param platform: ex: windows8-64, windows10-64
        @return:
        """
        platform_source_data = [item for item in self.source_data if
                                item.get(DashboardDataGenerator.KEY_PLATFORM) == platform]

        ret_obj = {}

        for casename in self.casename_set:
            casename_with_platform = '{}_{}'.format(casename, platform.split('-')[0])
            template = copy.deepcopy(DashboardDataGenerator.JS_DATA_TEMPLATE)

            template['title']['text'] = casename_with_platform

            #
            # handle Firefox
            #
            f_casename_platform_source_data = [item for item in platform_source_data
                                               if item.get(DashboardDataGenerator.KEY_CASENAME) == casename and
                                               item.get(
                                                   DashboardDataGenerator.KEY_BROWSER) == DashboardDataGenerator.BROWSER_FIREFOX]

            firefox_median_data_obj = copy.deepcopy(DashboardDataGenerator.JS_DATA_SERIES_MEDIAN_OBJ_TEMPLATE)
            firefox_median_data_obj['name'] = DashboardDataGenerator.BROWSER_FIREFOX_MEDIAN
            firefox_median_data_obj['color'] = DashboardDataGenerator.COLOR_FIREFOX
            firefox_median_data_obj['marker'] = {'symbol': DashboardDataGenerator.SYMBOL_FIREFOX}

            firefox_data_obj = copy.deepcopy(DashboardDataGenerator.JS_DATA_SERIES_OBJ_TEMPLATE)
            firefox_data_obj['name'] = DashboardDataGenerator.BROWSER_FIREFOX
            firefox_data_obj['color'] = DashboardDataGenerator.COLOR_FIREFOX_OPACITY
            firefox_data_obj['marker'] = {'symbol': DashboardDataGenerator.SYMBOL_FIREFOX}

            for data in f_casename_platform_source_data:
                timestamp_js = data.get(DashboardDataGenerator.KEY_TIMESTAMP_JS)
                value_list = data.get(DashboardDataGenerator.KEY_VALUE_LIST)

                if value_list:
                    # median_values is (timestamp, median value) tuple
                    firefox_median_data_obj['data'].append((timestamp_js, median(value_list)))

                for value in value_list:
                    firefox_data_obj['data'].append([timestamp_js, value])

            template['series'].append(firefox_data_obj)
            template['series'].append(firefox_median_data_obj)

            #
            # handle Chrome
            #
            c_casename_platform_source_data = [item for item in platform_source_data
                                               if item.get(DashboardDataGenerator.KEY_CASENAME) == casename and
                                               item.get(
                                                   DashboardDataGenerator.KEY_BROWSER) == DashboardDataGenerator.BROWSER_CHROME]

            chrome_median_data_obj = copy.deepcopy(DashboardDataGenerator.JS_DATA_SERIES_MEDIAN_OBJ_TEMPLATE)
            chrome_median_data_obj['name'] = DashboardDataGenerator.BROWSER_CHROME_MEDIAN
            chrome_median_data_obj['color'] = DashboardDataGenerator.COLOR_CHROME
            chrome_median_data_obj['marker'] = {'symbol': DashboardDataGenerator.SYMBOL_CHROME}

            chrome_data_obj = copy.deepcopy(DashboardDataGenerator.JS_DATA_SERIES_OBJ_TEMPLATE)
            chrome_data_obj['name'] = DashboardDataGenerator.BROWSER_CHROME
            chrome_data_obj['color'] = DashboardDataGenerator.COLOR_CHROME_OPACITY
            chrome_data_obj['marker'] = {'symbol': DashboardDataGenerator.SYMBOL_CHROME}

            for data in c_casename_platform_source_data:
                timestamp_js = data.get(DashboardDataGenerator.KEY_TIMESTAMP_JS)
                value_list = data.get(DashboardDataGenerator.KEY_VALUE_LIST)

                if value_list:
                    # median_values is (timestamp, median value) tuple
                    chrome_median_data_obj['data'].append((timestamp_js, median(value_list)))

                for value in value_list:
                    chrome_data_obj['data'].append([timestamp_js, value])

            template['series'].append(chrome_data_obj)
            template['series'].append(chrome_median_data_obj)

            ret_obj[casename_with_platform] = template

        return ret_obj

    def generate_build_overall_progress_via_platform_timestamp(self, platform, timestamp):
        """

        @param platform: ex: windows8-64, windows10-64
        @param timestamp:
        @return:
        """

        target_source_data = [item for item in self.source_data if
                              item.get(DashboardDataGenerator.KEY_PLATFORM) == platform and item.get(
                                  DashboardDataGenerator.KEY_TIMESTAMP) == timestamp]

        ret_obj = {}
        ret_obj[DashboardDataGenerator.KEY_OVERALL_CASES] = {}
        ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS] = {}

        # set revision
        ret_obj[DashboardDataGenerator.KEY_REVISON] = target_source_data[0].get(DashboardDataGenerator.KEY_REVISON)

        # Firefox and Chrome
        total_case_number = len(self.casename_set) * 2
        ret_obj[DashboardDataGenerator.KEY_OVERALL_TOTAL_CASE_NUMBER] = total_case_number

        SUITE_STATUS_SUCCESS = 0
        SUITE_STATUS_RUNNING = 1
        SUITE_STATUS_NO_RESULT = 2

        finished_counter = 0
        for casename in self.casename_set:
            ret_obj[DashboardDataGenerator.KEY_OVERALL_CASES][casename] = {}

            suite_name = casename.split('_')[0]
            if not ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS].get(suite_name):
                ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name] = {}

            #
            # handle Firefox
            #
            counter = 0
            f_result_data = [item for item in target_source_data
                             if item.get(DashboardDataGenerator.KEY_CASENAME) == casename and
                             item.get(
                                 DashboardDataGenerator.KEY_BROWSER) == DashboardDataGenerator.BROWSER_FIREFOX]
            for result_data in f_result_data:
                counter = counter + len(result_data[DashboardDataGenerator.KEY_VALUE_LIST])
            ret_obj[DashboardDataGenerator.KEY_OVERALL_CASES][casename][
                DashboardDataGenerator.BROWSER_FIREFOX] = counter

            # count all cases number
            if counter >= DashboardDataGenerator.RESULT_AMOUNT:
                finished_counter += 1

            # case suite status
            if not ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name].get(
                    DashboardDataGenerator.BROWSER_FIREFOX):
                ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name][
                    DashboardDataGenerator.BROWSER_FIREFOX] = SUITE_STATUS_SUCCESS

            if counter >= DashboardDataGenerator.RESULT_AMOUNT:
                current_case_status = SUITE_STATUS_SUCCESS
            elif 0 < counter < DashboardDataGenerator.RESULT_AMOUNT:
                current_case_status = SUITE_STATUS_RUNNING
            else:
                current_case_status = SUITE_STATUS_NO_RESULT
            ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name][DashboardDataGenerator.BROWSER_FIREFOX] = max(current_case_status, ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name][DashboardDataGenerator.BROWSER_FIREFOX])

            #
            # handle Chrome
            #
            counter = 0
            c_result_data = [item for item in target_source_data
                             if item.get(DashboardDataGenerator.KEY_CASENAME) == casename and
                             item.get(
                                 DashboardDataGenerator.KEY_BROWSER) == DashboardDataGenerator.BROWSER_CHROME]
            for result_data in c_result_data:
                counter = counter + len(result_data[DashboardDataGenerator.KEY_VALUE_LIST])
            ret_obj[DashboardDataGenerator.KEY_OVERALL_CASES][casename][
                DashboardDataGenerator.BROWSER_CHROME] = counter

            # count all cases number
            if counter >= DashboardDataGenerator.RESULT_AMOUNT:
                finished_counter += 1

            # case suite status
            if not ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name].get(
                    DashboardDataGenerator.BROWSER_CHROME):
                ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name][
                    DashboardDataGenerator.BROWSER_CHROME] = SUITE_STATUS_SUCCESS

            if counter >= DashboardDataGenerator.RESULT_AMOUNT:
                current_case_status = SUITE_STATUS_SUCCESS
            elif 0 < counter < DashboardDataGenerator.RESULT_AMOUNT:
                current_case_status = SUITE_STATUS_RUNNING
            else:
                current_case_status = SUITE_STATUS_NO_RESULT
            ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name][DashboardDataGenerator.BROWSER_CHROME] = max(current_case_status, ret_obj[DashboardDataGenerator.KEY_OVERALL_SUITE_STATUS][suite_name][DashboardDataGenerator.BROWSER_CHROME])

        ret_obj[DashboardDataGenerator.KEY_OVERALL_FINISH_CASE_NUMBER] = finished_counter
        percentage = float(finished_counter) / float(total_case_number)
        ret_obj[DashboardDataGenerator.KEY_OVERALL_FINISH_PERCENTAGE] = percentage

        # generate gauge object
        gauge_obj = copy.deepcopy(DashboardDataGenerator.JS_GAUGE_TEMPLATE)
        gauge_series_obj = copy.deepcopy(DashboardDataGenerator.JS_GAUGE_SERIES_OBJ_TEMPLATE)
        gauge_series_obj['name'] = platform
        gauge_series_obj['data'] = [int(percentage * 100)]
        gauge_obj['series'].append(gauge_series_obj)
        ret_obj[DashboardDataGenerator.KEY_OVERALL_GAUGE] = gauge_obj

        return ret_obj

    def generate_latest_build_overall_progress_for_platform(self, platform):
        """

        @param platform: ex: windows8-64, windows10-64
        @return:
        """
        return self.generate_build_overall_progress_via_platform_timestamp(platform=platform, timestamp=self.latest_timestamp)

    def run(self, gist_user_name=None, gist_auth_token=None):
        """
        Generate the dashboard data for "windows8-64" and "windows10-64" (platform = win64).
        @param gist_user_name:
        @param gist_auth_token:
        @return:
        """
        logging.info('Dashboard Data Generator starting ...')

        if not gist_user_name or not gist_auth_token:
            raise Exception('Please config "gist_user_name" and "gist_auth_token".')

        # init the source data
        self._generate_source_data()

        current_utc = datetime.utcnow()
        # the result of time.mktime(current_utc.timetuple()) is larger than utc_ts 28800 sec
        utc_ts = int((current_utc - datetime(1970, 1, 1, 0, 0, 0, 0)).total_seconds())
        cuttrnt_utc_timestamp = str(utc_ts)
        cuttrnt_utc_timestamp_js = utc_ts * 1000

        data_obj = {
            'cuttrnt_utc_timestamp': cuttrnt_utc_timestamp,
            'cuttrnt_utc_timestamp_js': cuttrnt_utc_timestamp_js,
            'latest_timestamp': self.latest_timestamp,
            'latest_timestamp_js': self.latest_timestamp_js,
            'windows8': self.generate_data_for_platform('windows8-64'),
            'windows10': self.generate_data_for_platform('windows10-64')
        }

        progress_obj = {
            'cuttrnt_utc_timestamp': cuttrnt_utc_timestamp,
            'cuttrnt_utc_timestamp_js': cuttrnt_utc_timestamp_js,
            'latest_timestamp': self.latest_timestamp,
            'latest_timestamp_js': self.latest_timestamp_js,
            'windows8': self.generate_latest_build_overall_progress_for_platform('windows8-64'),
            'windows10': self.generate_latest_build_overall_progress_for_platform('windows10-64')
        }

        # upload files to gist
        gist_obj = GISTUtil(gist_user_name, gist_auth_token)

        data_obj_string = json.dumps(data_obj).replace('\\', '\\\\').replace('"', '\\"')
        gist_obj.upload_content(input_file_name='win_dashboard_data.json', input_content=data_obj_string)
        logging.info('Dashboard Data Generator: win_dashboard_data.json uploaded.')

        progress_obj_string = json.dumps(progress_obj).replace('\\', '\\\\').replace('"', '\\"')
        gist_obj.upload_content(input_file_name='win_dashboard_progress.json', input_content=progress_obj_string)
        logging.info('Dashboard Data Generator: win_dashboard_progress.json uploaded.')

        logging.info('Dashboard Data Generator done.')


if __name__ == '__main__':
    app = DashboardDataGenerator()
    app.run(gist_user_name='foo', gist_auth_token='bar')
