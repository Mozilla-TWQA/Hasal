import os
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):

    def setUp(self):
        self.sikuli_script_path = os.getenv("SIKULI_SCRIPT_PATH")
        if self.sikuli_script_path.endswith(os.sep):
            sikuli_script_name = self.sikuli_script_path.split(os.sep)[-2].split(".")[0]
        else:
            sikuli_script_name = self.sikuli_script_path.split(os.sep)[-1].split(".")[0]

        # Init environment variables
        self.env.__init__(self._testMethodName, self._testMethodDoc, sikuli_script_name)

        super(TestSikuli, self).setUp()

    def test_pilot_run(self):
        self.round_status = self.sikuli.run_sikulix_cmd(self.sikuli_script_path)
