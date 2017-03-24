import time
import importlib


class Profilers(object):
    profiler_obj_list = []
    env = None

    def __init__(self, input_env, input_browser_type=None, input_sikuli_obj=None):
        self.browser_type = input_browser_type
        self.env = input_env
        self.sikuli = input_sikuli_obj

    # TODO: geckoProfiler and performanceTimingProfiler used Sikuli object
    def start_profiling(self, profiler_list):
        enabled_profiler_list = [x for x in profiler_list if profiler_list[x]['enable'] is True]
        for profiler_data in enabled_profiler_list:
            if 'path' in profiler_list[profiler_data]:
                profiler_class = getattr(importlib.import_module(profiler_list[profiler_data]['path']), profiler_data)
                profiler_obj = profiler_class(self.env, self.browser_type, self.sikuli)
                profiler_obj.start_recording()
                self.profiler_obj_list.append(profiler_obj)

    def stop_profiling(self, input_profile_dir_path=None):
        for profiler_obj in self.profiler_obj_list:
            profiler_obj.stop_recording(profile_path=input_profile_dir_path)

    def get_t1_time(self):
        t1_time = time.time()
        for profiler_obj in self.profiler_obj_list:
            if self.env.PROFILER_FLAG_AVCONV.lower() in profiler_obj.__class__.__name__.lower():
                t1_time = profiler_obj.t1_time
        return t1_time
