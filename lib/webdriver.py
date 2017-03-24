import time


class Webdriver():

    def __init__(self, driver):
        self.driver = driver

    @staticmethod
    def wait_for(condition_function):
        start_time = time.time()
        while time.time() < start_time + 10:
            if condition_function():
                return True
            else:
                time.sleep(0.1)
        raise Exception(
            'Timeout waiting for {}'.format(condition_function.__name__)
        )

    def page_has_loaded(self):
        page_state = self.driver.execute_script('return document.readyState;')
        return page_state == 'complete'

    def close_browser(self, browser):
        self.driver.close()
        self.driver.quit()
        pass

    def return_driver(self):
        return self.driver
