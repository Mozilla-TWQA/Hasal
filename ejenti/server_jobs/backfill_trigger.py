import os
import json
import random
import logging
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from lib.common.statusFileCreator import StatusFileCreator
from lib.helper.generateBackfillTableHelper import GenerateBackfillTableHelper
from lib.modules.build_information import BuildInformation
from lib.common.commonUtil import CommonUtil
from ejenti.pulse_modules.hasalPulsePublisher import HasalPulsePublisher


class BackFillTrigger(object):

    PLATFORM = 'win64'
    RESULT_AMOUNT = 6
    DEFAULT_WAIT_TIMEOUT_DELTA_HOUR = 6

    DEFAULT_CMD_CONFIG_FILE_PATH = os.path.join('configs', 'ejenti', 'cmd_config.json')

    DEFAULT_CMD = 'run-hasal-on-specify-nightly'
    KEY_OVERWRITE_HASAL_SUITE_CASE_LIST = 'OVERWRITE_HASAL_SUITE_CASE_LIST'
    KEY_DOWNLOAD_PKG_DIR_URL = 'DOWNLOAD_PKG_DIR_URL'
    KEY_DOWNLOAD_REVISION = 'DOWNLOAD_REVISION'

    KEY_PERFHERDER_DATA = 'perfherder_data'
    KEY_VALUE = 'value'

    BROWSER_FIREFOX = 'firefox'
    BROWSER_CHROME = 'chrome'

    PLATFORM_WIN7 = 'windows8-64'
    PLATFORM_WIN10 = 'windows10-64'

    PLATFORM_MAPPING = {
        'windows8-64': 'win7',
        'windows10-64': 'win10'
    }

    BACK_FILL_LOG = 'back_fill.log'

    def __init__(self):
        self.pulse_username = ''
        self.pulse_password = ''
        self.pulse_configs = {}
        self.casename_set = set()

        self.logger = logging.getLogger('Back_Fill')
        self.logger.setLevel(logging.DEBUG)

        # create Rotating File Handler, 1 day, backup 14 times.
        rotating_handler = TimedRotatingFileHandler(BackFillTrigger.BACK_FILL_LOG,
                                                    when='midnight',
                                                    interval=1,
                                                    backupCount=14)

        rotating_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s')
        rotating_handler.setFormatter(rotating_formatter)
        self.logger.addHandler(rotating_handler)

    def send_task_to_pulse(self, job_name, topic, real_casename, amount, build_info):
        job_id = StatusFileCreator.create_job_id_folder(job_name)
        job_id_fp = os.path.join(StatusFileCreator.get_status_folder(), job_id)
        # Recording Status
        StatusFileCreator.create_status_file(job_id_fp, StatusFileCreator.STATUS_TAG_PULSE_TRIGGER_BACKFILL, 100)

        # check queue
        queue_exists = HasalPulsePublisher.check_pulse_queue_exists(username=self.pulse_username,
                                                                    password=self.pulse_password,
                                                                    topic=topic)

        if not queue_exists:
            self.logger.error('There is not Queue for Topic [{topic}]. Message might be ignored.'.format(topic=topic))

        #
        # Pre-handle specify command
        # add "OVERWRITE_HASAL_SUITE_CASE_LIST", "DOWNLOAD_PKG_DIR_URL", and "DOWNLOAD_REVISION"
        #
        cmd_name = BackFillTrigger.DEFAULT_CMD
        overwrite_cmd_config = self.pulse_configs
        overwrite_cmd_config[BackFillTrigger.KEY_OVERWRITE_HASAL_SUITE_CASE_LIST] = real_casename
        overwrite_cmd_config[BackFillTrigger.KEY_DOWNLOAD_PKG_DIR_URL] = build_info.archive_url
        overwrite_cmd_config[BackFillTrigger.KEY_DOWNLOAD_REVISION] = build_info.revision

        command_config = CommonUtil.load_json_file(BackFillTrigger.DEFAULT_CMD_CONFIG_FILE_PATH)

        # Push MetaTask to Pulse
        publisher = HasalPulsePublisher(username=self.pulse_username,
                                        password=self.pulse_password,
                                        command_config=command_config)

        now = datetime.now()
        now_string = now.strftime('%Y-%m-%d_%H:%M:%S.%f')
        uid_prefix = '{time}.{job}'.format(time=now_string, job=job_name)
        # push meta task
        self.logger.info('Pushing to Pulse...\n'
                         '{line}\n'
                         'UID prefix: {uid_prefix}\n'
                         'Trigger Job: {job_name}\n'
                         'Topic: {topic}\n'
                         'Amount: {amount}\n'
                         'command {cmd}\n'
                         'cmd_config: {cmd_config}\n'
                         '{line}\n'.format(uid_prefix=uid_prefix,
                                           job_name=job_name,
                                           topic=topic,
                                           amount=amount,
                                           cmd=cmd_name,
                                           cmd_config=overwrite_cmd_config,
                                           line='-' * 10))
        uid_list = []
        for idx in range(amount):
            uid = '{prefix}.{idx}'.format(prefix=uid_prefix, idx=idx + 1)
            uid_list.append(uid)

            publisher.push_meta_task(topic=topic,
                                     command_name=cmd_name,
                                     overwrite_cmd_configs=overwrite_cmd_config,
                                     uid=uid)

        # Recording Status
        content = {
            'job_name': job_name,
            'topic': topic,
            'amount': amount,
            'cmd': cmd_name,
            'cmd_config': CommonUtil.mask_credential_value(overwrite_cmd_config),
            'task_uid_list': uid_list
        }
        StatusFileCreator.create_status_file(job_id_fp, StatusFileCreator.STATUS_TAG_PULSE_TRIGGER_BACKFILL, 900, content)

    def trigger_latest_back_fill(self, build_info, wait_timeout_hour=None):

        current_time = datetime.utcnow()
        build_time = datetime.strptime(build_info.archive_datetime, '%Y-%m-%d-%H-%M-%S')

        if wait_timeout_hour:
            timeout_hour = wait_timeout_hour
        else:
            timeout_hour = BackFillTrigger.DEFAULT_WAIT_TIMEOUT_DELTA_HOUR
        delta_hours = timedelta(hours=timeout_hour)
        if (current_time - build_time) > delta_hours:
            self.logger.info('Archive Build Time {bt}, the time delta is more than {timeout} hours ({delta}), run!'.format(bt=build_time, timeout=timeout_hour, delta=(current_time - build_time)))
        else:
            self.logger.info('Archive Build Time {bt}, the time delta is less than {timeout} hours ({delta}), skip.'.format(bt=build_time, timeout=timeout_hour, delta=(current_time - build_time)))
            return

        perf_data = build_info.perfherder_data

        ret_dict = {
            'win7': {},
            'win10': {}
        }

        for casename in self.casename_set:
            for browser in [BackFillTrigger.BROWSER_FIREFOX, BackFillTrigger.BROWSER_CHROME]:

                # ex: tests.regression.gmail.test_firefox_gmail_ail_compose_new_mail_via_keyboard
                suite_name = casename.split('_')[0]
                real_casename = 'tests.regression.{suite_name}.test_{browser}_{casename}'.format(
                    suite_name=suite_name,
                    browser=browser,
                    casename=casename)

                for platform in [BackFillTrigger.PLATFORM_WIN10, BackFillTrigger.PLATFORM_WIN7]:

                    # ex: gmail_ail_compose_new_mail_via_keyboard:firefox:windows10-64
                    key = '{c}:{b}:{p}'.format(c=casename, b=browser, p=platform)

                    detail = perf_data.get(key)
                    if detail:
                        value_list = detail.get(BackFillTrigger.KEY_VALUE)
                        if len(value_list) < BackFillTrigger.RESULT_AMOUNT:
                            backfill_amount = BackFillTrigger.RESULT_AMOUNT - len(value_list)
                        else:
                            backfill_amount = 0
                    else:
                        backfill_amount = BackFillTrigger.RESULT_AMOUNT

                    if backfill_amount > 0:
                        ret_dict[BackFillTrigger.PLATFORM_MAPPING.get(platform)][real_casename] = backfill_amount

        self.logger.debug('Back fill table:\n{}'.format(json.dumps(ret_dict, indent=2)))

        for topic, detail in ret_dict.items():

            real_casename_list = detail.keys()
            random.shuffle(real_casename_list)

            for real_casename in real_casename_list:
                amount = detail.get(real_casename)
                casename = real_casename.split('.')[-1]
                backfill_job_name = '{topic}_{case}'.format(topic=topic, case=casename)
                self.logger.debug('Back fill case [{}] with [{}] times. '.format(backfill_job_name, amount))

                self.send_task_to_pulse(job_name=backfill_job_name,
                                        topic=topic,
                                        real_casename=real_casename,
                                        amount=amount,
                                        build_info=build_info)

    def run(self, pulse_username='', pulse_password='', pulse_configs={}, wait_timeout_hour=None):
        """
        Generate the dashboard data for "windows8-64" and "windows10-64" (platform = win64).
        @return:
        """
        self.logger.info('Back Fill Trigger starting ...')

        if not pulse_username or not pulse_password or not pulse_configs:
            raise Exception('Please config "pulse_username", "pulse_password" and "pulse_configs" for back fill data.')
        self.pulse_username = pulse_username
        self.pulse_password = pulse_password
        self.pulse_configs = pulse_configs

        table_obj = GenerateBackfillTableHelper.get_history_archive_perfherder_relational_table(
            BackFillTrigger.PLATFORM)

        if table_obj:
            latest_28_timestamp_list = sorted(table_obj.keys())[-28:]

            # latest build timestamp
            latest_timestamp = latest_28_timestamp_list[-1]

            # except latest, other 27 build timestamp
            # latest_28_except_latest_timestamp_list = latest_28_timestamp_list[: -1]

            for timestamp in latest_28_timestamp_list:
                perf_data_obj_dict = table_obj.get(timestamp, {}).get(BackFillTrigger.KEY_PERFHERDER_DATA, {})
                for key, value in perf_data_obj_dict.items():
                    # ex: amazon_ail_type_in_search_field:firefox:windows8-64
                    casename, browser, platform = key.split(':')
                    self.casename_set.add(casename)

            latest_build_info = BuildInformation(table_obj.get(latest_timestamp))
            self.trigger_latest_back_fill(build_info=latest_build_info, wait_timeout_hour=wait_timeout_hour)

        self.logger.info('Back Fill Trigger done.')


if __name__ == '__main__':
    GenerateBackfillTableHelper.generate_archive_perfherder_relational_table(input_backfill_days=14, input_platform=BackFillTrigger.PLATFORM)

    default_log_format = '%(asctime)s %(levelname)s [%(name)s.%(funcName)s] %(message)s'
    default_datefmt = '%Y-%m-%d %H:%M'
    logging.basicConfig(level=logging.INFO, format=default_log_format, datefmt=default_datefmt)

    pulse_username = ''
    pulse_password = ''
    pulse_configs = {}

    app = BackFillTrigger()
    app.run(pulse_username=pulse_username, pulse_password=pulse_password, pulse_configs=pulse_configs)
