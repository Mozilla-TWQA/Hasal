class BaseProfiler(object):
    def __init__(self, input_env, input_browser_type=None, input_sikuli_obj=None):
        self.browser_type = input_browser_type
        self.env = input_env
        self.sikuli = input_sikuli_obj

    def stop_recording(self, **kwargs):
        pass
