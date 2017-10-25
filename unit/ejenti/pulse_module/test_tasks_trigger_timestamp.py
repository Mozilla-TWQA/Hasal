import os
import unittest

from ejenti.pulse_modules.tasksTrigger import TasksTrigger
from lib.helper.generateBackfillTableHelper import GenerateBackfillTableHelper
from lib.helper.perfherderDataQueryHelper import PerfherderDataQueryHelper


class TestTasksTriggerTimestamp(unittest.TestCase):

    def setUp(self):
        self.fake_job_name = 'unittest'
        self.target_platform = 'mac'
        self.query_days = 1

        TasksTrigger.clean_timestamp_by_job_name(self.fake_job_name)

        removed_file_list = [
            GenerateBackfillTableHelper.PLATFORM_BACKFILL_TABLE_LOCAL_FN.format(platform=self.target_platform),
            PerfherderDataQueryHelper.DEFAULT_HASAL_SIGNATURES]
        for removed_file in removed_file_list:
            if os.path.isfile(removed_file):
                os.remove(removed_file)

        # generate data for checking timestamp
        GenerateBackfillTableHelper.generate_archive_perfherder_relational_table(
            input_backfill_days=self.query_days, input_platform=self.target_platform)

    def test_check_latest_timestamp(self):
        ret = TasksTrigger.check_latest_timestamp(self.fake_job_name, self.target_platform)
        self.assertTrue(ret, 'First query should be True.')

        ret = TasksTrigger.check_latest_timestamp(self.fake_job_name, self.target_platform)
        self.assertFalse(ret, 'Second query should be False.')

    def tearDown(self):
        TasksTrigger.clean_timestamp_by_job_name(self.fake_job_name)


if __name__ == '__main__':
    unittest.main()
