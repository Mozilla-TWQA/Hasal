from base import BrowserBase


# TODO: need to be Webdriver triggered
class BrowserChrome(BrowserBase):
    default_tracing_capture_period = 900  # sec

    def launch(self):
        pass

    # TODO: do this in launch
    # TODO: inject environment variables
    # 1. Need to have width and height set & language as English(US)
    # [self.command, "--window-size=" + str(self.windows_size_width) + "," + str(self.window_size_height)]
    # TODO: driver.set_windows_size(self.windows_size_width, self.window_size_height)
    def get_browser_settings(self, **kwargs):
        if "tracing_path" in kwargs:
            self.launch_cmd.extend(["--trace-startup", "--trace-startup-file=" + kwargs['tracing_path'],
                                    "--trace-startup-duration=" + str(self.default_tracing_capture_period)])

    def get_version(self):
        pass

    def return_driver(self):
        return self.driver
