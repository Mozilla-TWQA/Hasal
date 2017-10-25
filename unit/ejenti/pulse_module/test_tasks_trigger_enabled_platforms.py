import os
import unittest

from ejenti.pulse_modules.tasksTrigger import TasksTrigger


class TestTasksTriggerEnabledPlatforms(unittest.TestCase):

    def setUp(self):
        self.fake_pass_job_config = {
            "mac": {
                "enable": True,
                "topic": "testing-darwin",
                "platform_build": "foo_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            },
            "mac2": {
                "enable": True,
                "topic": "testing-darwin",
                "platform_build": "foo_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            },
            "mac3": {
                "enable": True,
                "topic": "testing-darwin",
                "platform_build": "bar_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            },
            "mac4": {
                "enable": False,
                "topic": "testing-darwin",
                "platform_build": "BAD_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            }
        }
        self.fake_fail_job_config = {
            "mac": {
                "enable": True,
                "topic": "testing-darwin",
                "platform_build": "foo_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            },
            "mac2": {
                "enable": True,
                "topic": "testing-darwin",
                "platform_build": "foo_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            },
            "mac3": {
                "enable": True,
                "topic": "testing-darwin",
                "platform_build": "bar_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            },
            "mac4": {
                "enable": True,
                "topic": "testing-darwin",
                "platform_build": "BAD_platform",
                "interval_minutes": 1,
                "amount": 1,
                "cmd": "download-latest-nightly",
                "configs": {}
            }
        }

    def test_get_enabled_platform_list_from_trigger_jobs_config_pass(self):
        expected_ret = ['foo_platform', 'bar_platform']
        ret = TasksTrigger.get_enabled_platform_list_from_trigger_jobs_config(self.fake_pass_job_config)
        self.assertEqual(expected_ret, ret)

    def test_get_enabled_platform_list_from_trigger_jobs_config_fail(self):
        expected_ret = ['foo_platform', 'bar_platform']
        ret = TasksTrigger.get_enabled_platform_list_from_trigger_jobs_config(self.fake_fail_job_config)
        self.assertNotEqual(expected_ret, ret)


if __name__ == '__main__':
    unittest.main()
