import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from base import BrowserBase
from ..common.logConfig import get_logger

logger = get_logger(__name__)


class BrowserFirefox(BrowserBase):

    def launch(self):
        # TODO: temporary solution here. need to have it set up in bootstrap
        os.environ['PATH'] += ":/home/hasal/Hasal/thirdParty/geckodriver"
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

