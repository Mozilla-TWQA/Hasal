import importlib


class Profilers(object):
    profiler_obj_list = []
    env = None

    def __init__(self, input_env):
        self.env = input_env

    def start_profiling(self, profiler_list):
        for profiler_data in profiler_list:
            profiler_class = getattr(importlib.import_module(profiler_data['path']), profiler_data['name'])
            profiler_obj = profiler_class(self.env)
            profiler_obj.start_recording()
            self.profiler_obj_list.append(profiler_obj)

    def stop_profiling(self):
        for profiler_obj in self.profiler_obj_list:
            profiler_obj.stop_recording()
