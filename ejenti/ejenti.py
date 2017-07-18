"""liholiho.

Usage:
  liholiho.py [--cmd-config=<str>] [--job-config=<str>] [--config=<str>]
  liholiho.py (-h | --help)

Options:
  -h --help                       Show this screen.
  --config=<str>                  Specify the config.json file path. [default: config.json]
  --cmd-config=<str>              Specify the cmd_config.json file path. [default: cmd_config.json]
  --job-config=<str>              Specify the job_config.json file path. [default: job_config.json]
"""
import re
import time
import importlib
from lib.common.commonUtil import CommonUtil
from docopt import docopt
from apscheduler.schedulers.background import BackgroundScheduler
from multiprocessing import Manager


class MainRunner(object):

    def __init__(self, cmd_config_fp, job_config_fp, config_fp):

        # load configuration json files
        self.cmd_config = CommonUtil.load_json_file(cmd_config_fp)
        self.job_config = CommonUtil.load_json_file(job_config_fp)
        self.config = CommonUtil.load_json_file(config_fp)

        # init schedulers
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_jobstore('sqlalchemy', url=self.config['job_store_url'])
        self.scheduler.start()

        # init variables
        mananger = Manager()
        self.sync_queue = mananger.Queue()
        self.async_queue = mananger.Queue()
        self.current_job_list = []

    def cmd_queue_composer(self, input_cmd_str):
        current_command = None
        for cmd_pattern in self.cmd_config['cmd-settings']:
            re_compile_obj = re.compile(cmd_pattern)
            re_match_obj = re_compile_obj.search(input_cmd_str)
            if re_match_obj:
                current_command = cmd_pattern
                print current_command
                break

    def load_default_jobs(self, input_scheduler, input_job_config):
        current_jobs = input_scheduler.get_jobs()
        current_jobs_name = [job.name for job in current_jobs]
        for job_name in input_job_config:
            if input_job_config[job_name]['default-loaded']:
                if job_name not in current_jobs_name:
                    func_point = getattr(importlib.import_module(input_job_config[job_name]['module-path']), job_name)
                    self.scheduler.add_job(func_point, input_job_config[job_name]['trigger-type'], seconds=input_job_config[job_name]['interval'], kwargs={'async_queue': self.async_queue, 'sync_queue': self.sync_queue, 'configs': input_job_config[job_name]['configs']})

    def run(self):
        # load default job into scheduler if the job is not exist
        self.load_default_jobs(self.scheduler, self.job_config)

        # enter the loop to receive the interactive command
        while True:
            # user_input = raw_input()
            time.sleep(3)


def main():
    arguments = docopt(__doc__)
    objRunner = MainRunner(arguments['--cmd-config'], arguments['--job-config'], arguments['--config'])
    objRunner.run()


if __name__ == '__main__':
    main()
