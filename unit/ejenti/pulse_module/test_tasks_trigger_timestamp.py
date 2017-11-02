import unittest
from mock import patch

from ejenti.pulse_modules.tasksTrigger import TasksTrigger


class TestTasksTriggerTimestamp(unittest.TestCase):

    def setUp(self):
        self.fake_job_name = 'unittest_tasks_trigger_timestamp'
        TasksTrigger.clean_timestamp_by_job_name(self.fake_job_name)

    @patch('lib.helper.generateBackfillTableHelper.GenerateBackfillTableHelper.get_history_archive_perfherder_relational_table')
    def test_check_latest_timestamp(self, mock_method):
        mock_method.return_value = {
            "1508923859": {
                "archive_datetime": "2017-10-25-10-04-49",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/10/2017-10-25-10-04-49-mozilla-central/",
                "archive_dir": "2017-10-25-10-04-49-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/10/2017-10-25-10-04-49-mozilla-central/firefox-58.0a1.en-US.linux-x86_64.tar.bz2",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/10/2017-10-25-10-04-49-mozilla-central/firefox-58.0a1.en-US.linux-x86_64.json",
                "revision": "e56ae7213756d93da1c1c72805c8f8b8ddb9dcdd",
                "perfherder_data": {}
            },
            "1508970179": {
                "archive_datetime": "2017-10-25-23-04-40",
                "archive_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/10/2017-10-25-23-04-40-mozilla-central/",
                "archive_dir": "2017-10-25-23-04-40-mozilla-central/",
                "pkg_fn_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/10/2017-10-25-23-04-40-mozilla-central/firefox-58.0a1.en-US.linux-x86_64.tar.bz2",
                "pkg_json_url": "https://archive.mozilla.org/pub/firefox/nightly/2017/10/2017-10-25-23-04-40-mozilla-central/firefox-58.0a1.en-US.linux-x86_64.json",
                "revision": "64bab5cbb9b63808d04babfbcfba3175fd99f69d",
                "perfherder_data": {}
            }
        }

        target_platform = 'linux64'

        ret, build_info = TasksTrigger.check_latest_timestamp(self.fake_job_name, target_platform)
        self.assertTrue(ret, 'First query should be True.')

        expected_datetime = '2017-10-25-23-04-40'
        self.assertEqual(expected_datetime, build_info.archive_datetime)

        expected_revision = '64bab5cbb9b63808d04babfbcfba3175fd99f69d'
        self.assertEqual(expected_revision, build_info.revision)

        ret, build_info = TasksTrigger.check_latest_timestamp(self.fake_job_name, target_platform)
        self.assertFalse(ret, 'Second query should be False.')

        self.assertIsNone(build_info, 'BuildInfo of second query should be None.')

    def tearDown(self):
        TasksTrigger.clean_timestamp_by_job_name(self.fake_job_name)


if __name__ == '__main__':
    unittest.main()
