import os
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def test_firefox_pilot_run(self):
        self.sikuli_status = self.sikuli.run_sikulix_cmd( os.getenv("SIKULI_SCRIPT_PATH"))
