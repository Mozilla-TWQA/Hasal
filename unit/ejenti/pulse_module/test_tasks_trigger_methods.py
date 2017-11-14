import unittest

from ejenti.pulse_modules.tasksTrigger import TasksTrigger
from lib.modules.build_information import BuildInformation


class TestTasksTriggerMethods(unittest.TestCase):

    def test_get_enabled_platform_list_from_trigger_jobs_config_pass(self):
        fake_pass_job_config = {
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

        # adding "win64" as default enabled platform
        expected_ret = ['win64', 'foo_platform', 'bar_platform']
        ret = TasksTrigger.get_enabled_platform_list_from_trigger_jobs_config(fake_pass_job_config)
        self.assertEqual(expected_ret, ret)

    def test_get_enabled_platform_list_from_trigger_jobs_config_fail(self):
        fake_fail_job_config = {
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

        expected_ret = ['foo_platform', 'bar_platform']
        ret = TasksTrigger.get_enabled_platform_list_from_trigger_jobs_config(fake_fail_job_config)
        self.assertNotEqual(expected_ret, ret)

    def test_filter_cmd_config(self):
        fake_upload_config = {
            "CHECKOUT_LATEST_CODE_REMOTE_URL": "https://github.com/Mozilla-TWQA/Hasal.git",
            "CHECKOUT_LATEST_CODE_BRANCH_NAME": "dev",
            "OVERWRITE_HASAL_SUITE_CASE_LIST": "foo,bar,test",
            "OVERWIRTE_HASAL_CONFIG_CTNT": {
                "configs": {
                    "firefox": {
                        "obs_on_windows.json": {}
                    },
                    "index": {
                        "inputLatencyAnimationDctGenerator.json": {}
                    },
                    "upload": {
                        "fake.json": {
                            "enable": True,
                            "perfherder-protocol": "https",
                            "perfherder-host": "treeherder.allizom.org",
                            "perfherder-client-id": "ERROR",
                            "perfherder-secret": "ERROR",
                            "perfherder-repo": "mozilla-central"
                        }
                    }
                }
            }
        }

        ret = TasksTrigger.filter_cmd_config(fake_upload_config)

        expected_case = ['foo', 'bar', 'test']
        ret_case = ret['OVERWRITE_HASAL_SUITE_CASE_LIST']
        self.assertEqual(expected_case, ret_case)

        expected_id = 'hidden_credential_value'
        ret_id = ret['OVERWIRTE_HASAL_CONFIG_CTNT']['configs']['upload']['fake.json']['perfherder-client-id']
        self.assertEqual(expected_id, ret_id)

        expected_sec = 'hidden_credential_value'
        ret_sec = ret['OVERWIRTE_HASAL_CONFIG_CTNT']['configs']['upload']['fake.json']['perfherder-secret']
        self.assertEqual(expected_sec, ret_sec)

    def test_handle_specify_commands(self):
        fake_cmd_name = 'run-hasal-on-specify-nightly'
        fake_build_info = BuildInformation({
            'archive_datetime': '123456789',
            'archive_url': 'https://archive/url/',
            'archive_dir': 'https://archive/dir/',
            'pkg_fn_url': 'https://package/file/url/',
            'pkg_json_url': 'https://package/json/url/',
            'revision': 'fake_revision_foo',
            'perfherder_data': {}
        })
        input_cmd_configs = {
            'FOO': 'foo',
            'BAR': 'bar'
        }
        expect_cmd_configs = {
            'FOO': 'foo',
            'BAR': 'bar',
            'DOWNLOAD_PKG_DIR_URL': fake_build_info.archive_url,
            'DOWNLOAD_REVISION': fake_build_info.revision
        }
        ret = TasksTrigger.handle_specify_commands(fake_cmd_name, input_cmd_configs, fake_build_info)
        self.assertEqual(expect_cmd_configs, ret)


if __name__ == '__main__':
    unittest.main()
