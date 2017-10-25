import os
import unittest

from ejenti.pulse_modules.tasksTrigger import TasksTrigger


class TestTasksTriggerFilterCmdConfig(unittest.TestCase):

    def setUp(self):
        self.fake_upload_config = {
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

    def test_filter_cmd_config(self):
        ret = TasksTrigger.filter_cmd_config(self.fake_upload_config)

        expected_case = ['foo', 'bar', 'test']
        ret_case = ret['OVERWRITE_HASAL_SUITE_CASE_LIST']
        self.assertEqual(expected_case, ret_case)

        expected_id = '*****'
        ret_id = ret['OVERWIRTE_HASAL_CONFIG_CTNT']['configs']['upload']['fake.json']['perfherder-client-id']
        self.assertEqual(expected_id, ret_id)

        expected_sec = '*****'
        ret_sec = ret['OVERWIRTE_HASAL_CONFIG_CTNT']['configs']['upload']['fake.json']['perfherder-secret']
        self.assertEqual(expected_sec, ret_sec)


if __name__ == '__main__':
    unittest.main()
