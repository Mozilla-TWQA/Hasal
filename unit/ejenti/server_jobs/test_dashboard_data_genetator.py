import unittest
from mock import patch

from ejenti.server_jobs.dashboard_data_generator import DashbaordDataGenerator


class TestTasksTriggerMethods(unittest.TestCase):

    def test_run_without_gist_info(self):
        app = DashbaordDataGenerator()
        with self.assertRaises(Exception) as e:
            app.run(None)
        self.assertEqual(e.exception.message, 'Please config "gist_user_name" and "gist_auth_token".')

    @patch('lib.helper.generateBackfillTableHelper.GenerateBackfillTableHelper.get_history_archive_perfherder_relational_table')
    def test_generate_source_data(self, mock_method):
        mock_method.return_value = {
            "1510091849": {
                "archive_datetime": "2017-11-07-22-01-15",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/",
                "archive_dir": "2017-11-07-22-01-15-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/firefox-58.0a1.en-US.win64.zip",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/firefox-58.0a1.en-US.win64.json",
                "perfherder_data": {
                    "foo_ail_type_in_search_field:chrome:windows10-64": {
                        "value": [
                            5.56,
                            5.56
                        ],
                        "signature": "sig_foo_chrome_win10"
                    },
                    "foo_ail_type_in_search_field:firefox:windows10-64": {
                        "value": [
                            5.56
                        ],
                        "signature": "sig_foo_firefox_win10"
                    }
                },
                "revision": "rev_1510091849"
            },
            "1510138316": {
                "archive_datetime": "2017-11-08-11-08-38",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/",
                "archive_dir": "2017-11-08-11-08-38-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/firefox-58.0a1.en-US.win64.zip",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/firefox-58.0a1.en-US.win64.json",
                "perfherder_data": {
                    "foo_ail_type_in_search_field:chrome:windows10-64": {
                        "value": [
                            5.56
                        ],
                        "signature": "sig_foo_chrome_win10"
                    },
                    "foo_ail_type_in_search_field:firefox:windows10-64": {
                        "value": [
                            11.11,
                            5.56,
                            22.22
                        ],
                        "signature": "sig_foo_firefox_win10"
                    }
                },
                "revision": "rev_1510138316"
            }
        }

        expected_ret = [
            {
                'timestamp': '1510091849',
                'timestamp_js': 1510091849000,
                'casename': 'foo_ail_type_in_search_field',
                'browser': 'chrome',
                'platform': 'windows10-64',
                'value_list': [5.56, 5.56],
                'revision': 'rev_1510091849',
                'signature': 'sig_foo_chrome_win10'
            },
            {
                'timestamp': '1510091849',
                'timestamp_js': 1510091849000,
                'casename': 'foo_ail_type_in_search_field',
                'browser': 'firefox',
                'platform': 'windows10-64',
                'value_list': [5.56, ],
                'revision': 'rev_1510091849',
                'signature': 'sig_foo_firefox_win10'
            },
            {
                'timestamp': '1510138316',
                'timestamp_js': 1510138316000,
                'casename': 'foo_ail_type_in_search_field',
                'browser': 'chrome',
                'platform': 'windows10-64',
                'value_list': [5.56, ],
                'revision': 'rev_1510138316',
                'signature': 'sig_foo_chrome_win10'
            },
            {
                'timestamp': '1510138316',
                'timestamp_js': 1510138316000,
                'casename': 'foo_ail_type_in_search_field',
                'browser': 'firefox',
                'platform': 'windows10-64',
                'value_list': [11.11, 5.56, 22.22],
                'revision': 'rev_1510138316',
                'signature': 'sig_foo_firefox_win10'
            }
        ]

        app = DashbaordDataGenerator()
        ret_list = app._generate_source_data()
        self.assertEqual(expected_ret, ret_list)

    @patch('lib.helper.generateBackfillTableHelper.GenerateBackfillTableHelper.get_history_archive_perfherder_relational_table')
    def test_generate_data_for_platform(self, mock_method):
        mock_method.return_value = {
            "1510091849": {
                "archive_datetime": "2017-11-07-22-01-15",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/",
                "archive_dir": "2017-11-07-22-01-15-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/firefox-58.0a1.en-US.win64.zip",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/firefox-58.0a1.en-US.win64.json",
                "perfherder_data": {
                    "foo_ail_type_in_search_field:chrome:windows10-64": {
                        "value": [
                            5.56,
                            5.56
                        ],
                        "signature": "sig_foo_chrome_win10"
                    },
                    "foo_ail_type_in_search_field:firefox:windows10-64": {
                        "value": [
                            5.56
                        ],
                        "signature": "sig_foo_firefox_win10"
                    }
                },
                "revision": "rev_1510091849"
            },
            "1510138316": {
                "archive_datetime": "2017-11-08-11-08-38",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/",
                "archive_dir": "2017-11-08-11-08-38-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/firefox-58.0a1.en-US.win64.zip",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/firefox-58.0a1.en-US.win64.json",
                "perfherder_data": {
                    "foo_ail_type_in_search_field:chrome:windows10-64": {
                        "value": [
                            5.56
                        ],
                        "signature": "sig_foo_chrome_win10"
                    },
                    "foo_ail_type_in_search_field:firefox:windows10-64": {
                        "value": [
                            11.11,
                            5.56,
                            22.22
                        ],
                        "signature": "sig_foo_firefox_win10"
                    }
                },
                "revision": "rev_1510138316"
            }
        }

        expected_ret = {
            'foo_ail_type_in_search_field_windows10': {
                'title': {
                    'text': 'foo_ail_type_in_search_field_windows10'
                },
                'series': [
                    {'data': [[1510091849000, 5.56], [1510138316000, 11.11], [1510138316000, 5.56],
                              [1510138316000, 22.22]], 'name': 'firefox'},
                    {'data': [[1510091849000, 5.56], [1510091849000, 5.56], [1510138316000, 5.56]], 'name': 'chrome'}],
                'yAxis': {
                    'title': {'text': 'Asynchronize Input latency (ms)'},
                    'min': 0
                },
                'chart': {'type': 'spline'},
                'tooltip': {
                    'headerFormat': '<b>{series.name}</b><br>',
                    'pointFormat': '{point.x:%e. %b, %H:%M} - {point.y:.2f} ms'
                },
                'plotOptions': {'spline': {'marker': {'enabled': True}}},
                'xAxis': {
                    'type': 'datetime',
                    'dateTimeLabelFormats': {'month': '%e. %b', 'year': '%b'},
                    'title': {'text': 'Date'}
                }
            }
        }

        target_platform = 'windows10-64'
        app = DashbaordDataGenerator()
        ret_obj = app.generate_data_for_platform(target_platform)
        self.assertEqual(expected_ret, ret_obj)

    @patch('lib.helper.generateBackfillTableHelper.GenerateBackfillTableHelper.get_history_archive_perfherder_relational_table')
    def test_generate_latest_build_overall_progress_for_platform(self, mock_method):
        mock_method.return_value = {
            "1510091849": {
                "archive_datetime": "2017-11-07-22-01-15",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/",
                "archive_dir": "2017-11-07-22-01-15-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/firefox-58.0a1.en-US.win64.zip",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-07-22-01-15-mozilla-central/firefox-58.0a1.en-US.win64.json",
                "perfherder_data": {
                    "foo_ail_type_in_search_field:chrome:windows10-64": {
                        "value": [
                            5.56,
                            5.56
                        ],
                        "signature": "sig_foo_chrome_win10"
                    },
                    "foo_ail_type_in_search_field:firefox:windows10-64": {
                        "value": [
                            5.56
                        ],
                        "signature": "sig_foo_firefox_win10"
                    }
                },
                "revision": "rev_1510091849"
            },
            "1510138316": {
                "archive_datetime": "2017-11-08-11-08-38",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/",
                "archive_dir": "2017-11-08-11-08-38-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/firefox-58.0a1.en-US.win64.zip",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/11/2017-11-08-11-08-38-mozilla-central/firefox-58.0a1.en-US.win64.json",
                "perfherder_data": {
                    "foo_ail_type_in_search_field:chrome:windows10-64": {
                        "value": [
                            5.56
                        ],
                        "signature": "sig_foo_chrome_win10"
                    },
                    "foo_ail_type_in_search_field:firefox:windows10-64": {
                        "value": [
                            11.11,
                            5.56,
                            22.22
                        ],
                        "signature": "sig_foo_firefox_win10"
                    },
                    "bar_ail_type_in_search_field:chrome:windows10-64": {
                        "value": [
                            5.56,
                            5.56,
                            5.56,
                            5.56,
                            5.56,
                            5.56
                        ],
                        "signature": "sig_foo_chrome_win10"
                    },
                    "bar_ail_type_in_search_field:firefox:windows10-64": {
                        "value": [
                            5.56,
                            5.56,
                            5.56,
                            5.56,
                            5.56,
                            5.56,
                            5.56
                        ],
                        "signature": "sig_foo_firefox_win10"
                    }
                },
                "revision": "rev_1510138316"
            }
        }

        expected_ret = {
            'total_case_number': 4,
            'finish_percentage': 0.5,
            'finish_case_number': 2,
            'cases': {
                'foo_ail_type_in_search_field': {
                    'chrome': 1,
                    'firefox': 3
                },
                'bar_ail_type_in_search_field': {
                    'chrome': 6,
                    'firefox': 7
                }
            },
            'suite_status': {
                'foo': {
                    'chrome': 1,
                    'firefox': 1
                },
                'bar': {
                    'chrome': 0,
                    'firefox': 0
                }
            },
            'gauge': {
                'series': [
                    {
                        'data': [50],
                        'name': 'windows10-64',
                        'tooltip': {'valueSuffix': ''},
                        'dataLabels': {
                            'format': '<div style="text-align:center"><span style="font-size:25px;color:silver">{y}%</span></div>'
                        }
                    }
                ],
                'yAxis': {
                    'labels': {'enabled': False},
                    'tickWidth': 0,
                    'min': 0,
                    'max': 100,
                    'tickPixelInterval': 0,
                    'stops': [[0.1, '#ff0000'], [0.5, '#ffff00'], [0.9, '#00ff00']],
                    'tickAmount': 0,
                    'minorTickInterval': None,
                    'lineWidth': 0,
                    'tickInterval': 0.01
                },
                'title': None,
                'chart': {'type': 'solidgauge', 'backgroundColor': '#1a1a1a'},
                'tooltip': {'enabled': False},
                'credits': {'enabled': False},
                'plotOptions': {'solidgauge': {'dataLabels': {'y': 5, 'borderWidth': 0, 'useHTML': True}}},
                'pane': {
                    'endAngle': 90,
                    'size': '200%',
                    'center': ['50%', '100%'],
                    'background': {'outerRadius': '100%', 'innerRadius': '60%', 'shape': 'arc',
                                   'backgroundColor': '#1a1a1a'},
                    'startAngle': -90
                }
            }
        }

        target_platform = 'windows10-64'
        app = DashbaordDataGenerator()
        ret_obj = app.generate_latest_build_overall_progress_for_platform(target_platform)
        self.assertEqual(expected_ret, ret_obj)
