import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from base import BrowserBase
from ..common.logConfig import get_logger
from ..common.environment import Environment

logger = get_logger(__name__)


class BrowserFirefox(BrowserBase):

    def launch(self):
        # adding geckoprofiler path
        if Environment.DEFAULT_GECKODRIVER_DIR not in os.environ['PATH']:
            if self.current_platform_name == "darwin" or self.current_platform_name == "linux2":
                os.environ['PATH'] += ":" + Environment.DEFAULT_GECKODRIVER_DIR
            else:
                os.environ['PATH'] += ";" + Environment.DEFAULT_GECKODRIVER_DIR + ";"

        # set tracelogger environment variable for Webdriver
        # if "tracelogger" in kwargs:
        #     os.environ['TLLOG'] = "default"
        #     os.environ['TLOPTIONS'] = "EnableMainThread,EnableOffThread,EnableGraph"

        # set firefox profile path if self.profile_path is set
        if self.profile_path:
            firefox_profile = FirefoxProfile(self.profile_path)
            logger.info('Running Firefox with profile: {}'.format(self.profile_path))
            self.driver = webdriver.Firefox(firefox_profile=firefox_profile)
        else:
            logger.info('Running Firefox with default profile.')
            self.driver = webdriver.Firefox()

        WebDriverWait(self.driver, 10)
        self.driver.set_window_size(self.windows_size_width, self.window_size_height)

    def get_version(self):
        return self.driver.capabilities['browserVersion']

    def return_driver(self):
        return self.driver
