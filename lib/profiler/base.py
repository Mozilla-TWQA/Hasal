class BaseProfiler(object):
    def __init__(self, input_env, input_index_config, input_exec_config, input_browser_type=None, input_sikuli_obj=None):
        self.browser_type = input_browser_type
        self.env = input_env
        self.input_index_config = input_index_config
        self.exec_config = input_exec_config
        self.sikuli = input_sikuli_obj

    def stop_recording(self, **kwargs):
        pass
