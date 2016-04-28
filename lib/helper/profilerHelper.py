import os
import importlib


class Profilers(object):
    profiler_obj_list = []
    env = None

    def __init__(self, input_env, input_browser_type=None, input_sikuli_obj=None):
        self.browser_type = input_browser_type
        self.env = input_env
        self.sikuli = input_sikuli_obj

    def start_profiling(self, profiler_list):
        self.profiler_list = profiler_list
        for profiler_data in self.profiler_list:
            profiler_class = getattr(importlib.import_module(profiler_data['path']), profiler_data['name'])
            profiler_obj = profiler_class(self.env, self.browser_type, self.sikuli)
            profiler_obj.start_recording()
            self.profiler_obj_list.append(profiler_obj)

    def stop_profiling(self):
        for profiler_obj in self.profiler_obj_list:
            profiler_obj.stop_recording()

    def get_profile_path(self):
        enable_profile_count = 0
        return_profile_name = None
        for profiler_data in self.profiler_list:
            if profiler_data['name'] == "GeckoProfiler" or profiler_data['name'] == "HarProfiler":
                enable_profile_count += 1
                return_profile_name = profiler_data['profile_name']

        if enable_profile_count == 2:
            return os.path.join(self.env.DEFAULT_PROFILE_DIR, self.env.PROFILE_NAME_AUTOSAVEHAR_GECKOPROFILER)
        else:
            if return_profile_name is None:
                return return_profile_name
            else:
                return os.path.join(self.env.DEFAULT_PROFILE_DIR, return_profile_name)
