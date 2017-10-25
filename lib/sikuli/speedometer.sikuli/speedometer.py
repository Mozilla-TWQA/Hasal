from sikuli import *  # NOQA
import os
from common import WebApp


class speedometer(WebApp):
    # This is the new way of looping patterns of different operating systems.

    SPEEDOMETER_START_TEST_ICON = [
        [os.path.join('pics', 'speedometer_start_test_icon.png'), 25, 0]
    ]

    SPEEDOMETER_TEST_FINISH_ICON = [
        [os.path.join('pics', 'speedometer_test_finish_icon.png'), 0, 0]
    ]

    SPEEDOMETER_TEST_RESULT_DETAILS_ICON = [
        [os.path.join('pics', 'speedometer_test_finish_icon.png'), 100, 0]
    ]

    SPEEDOMETER_FOCUS_TEST_RESULT_DETAILS = [
        [os.path.join('pics', 'speedometer_test_finish_icon.png'), 0, -100]
    ]

    def wait_for_loaded(self, similarity=0.70):
        """
        Wait for speedometer loaded, max 15 sec
        @param similarity: The similarity of speedometer start test icon component. Default: 0.70.
        """
        return self._wait_for_loaded(component=speedometer.SPEEDOMETER_START_TEST_ICON, similarity=similarity, timeout=15)

    def wait_for_test_finish(self, similarity=0.80, timeout=600):
        return self._wait_for_loaded(component=speedometer.SPEEDOMETER_TEST_FINISH_ICON, similarity=similarity,
                                     timeout=timeout)

    def start_test(self):
        return self._click(action_name='Start Test', component=speedometer.SPEEDOMETER_START_TEST_ICON, wait_component=speedometer.SPEEDOMETER_START_TEST_ICON)

    def click_test_result_details(self, similarity=0.80):
        return self._click(action_name='Click Details',
                           component=speedometer.SPEEDOMETER_TEST_RESULT_DETAILS_ICON,
                           similarity=similarity,
                           wait_component=speedometer.SPEEDOMETER_TEST_RESULT_DETAILS_ICON)

    def copy_detail_information_to_clipboard(self, similarity=0.80):
        self._click(action_name='Click Details', component=speedometer.SPEEDOMETER_FOCUS_TEST_RESULT_DETAILS,
                    similarity=similarity,
                    wait_component=speedometer.SPEEDOMETER_FOCUS_TEST_RESULT_DETAILS)
        sleep(1)
        self.common.select_all()
        sleep(1)
        self.common.copy()
