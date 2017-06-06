import os
import sys
import time
import json
import shutil

DEFAULT_CHECK_ENV_KEY_LIST = ['OUTPUTLOC', 'HASAL_WORKSPACE', 'WORKSPACE', 'BUILD_NUMBER']
DEFAULT_AGENT_JOB_STATUS = {'BEGIN': 'begin', 'FINISH': 'finish', 'EXCEPTION': 'exception'}
DEFAULT_JOB_START_TIMEOUT = 120
DEFAULT_SLEEP_TIME = 3


def printlog(job_log_fp, current_line_no=0):
    if os.path.exists(job_log_fp):
        with open(job_log_fp) as read_fh:
            current_content = read_fh.readlines()
            if current_line_no < len(current_content):
                for content in current_content[current_line_no - 1:]:
                    print content.strip()
                    current_line_no = len(current_content)
            else:
                print "INFO: didn't get the new log from log file [%s]" % job_log_fp
                print "INFO: job log current line no [%s] over or equal to the job log total length [%s]" % (str(current_line_no), str(len(current_content)))
    else:
        print "WARNING: job log [%s] is not created yet!" % job_log_fp
    return current_line_no

# check environment key fit to our need
for check_key in DEFAULT_CHECK_ENV_KEY_LIST:
    if check_key not in os.environ:
        print "ERROR: Cannot get environments variable [%s]" % check_key
        sys.exit(1)

# init variables
current_build_tag = os.environ["BUILD_TAG"]
job_log_full_path = os.environ["OUTPUTLOC"]  # hasal/job.log
agent_trigger_conf_fn = current_build_tag + ".json"
agent_trigger_conf_fp = os.path.join(os.environ["HASAL_WORKSPACE"], "agent", agent_trigger_conf_fn)
jenkins_conf_path = os.path.join(os.environ["WORKSPACE"], agent_trigger_conf_fn)  # slave machine's jenkins folder
jenkins_job_log_path = os.path.join(os.environ["WORKSPACE"], os.path.basename(os.environ["OUTPUTLOC"]))
agent_status_dir_path = os.path.join(os.environ["HASAL_WORKSPACE"], "agent_status")
job_start_retry = 0
job_start_flag = 0
job_log_current_lineno = 1

# init environment
if os.path.exists(agent_status_dir_path) is False:
    print "ERROR: Cannot find the agent_status in your Hasal workding directory!"
    sys.exit(1)
if os.path.exists(jenkins_job_log_path):
    os.remove(jenkins_job_log_path)
if os.path.exists(jenkins_conf_path):
    os.remove(jenkins_conf_path)

# Main Program
while True:

    # extract job id from agent_status dir
    print "INFO: Monitor the agent status folder [%s]" % agent_status_dir_path
    agent_status_file_list = os.listdir(agent_status_dir_path)
    print "DEBUG: current agent status file list [%s]" % agent_status_file_list
    job_id_list = []
    for job_id in [os.path.splitext(id)[0] for id in agent_status_file_list]:
        if job_id not in job_id_list:
            job_id_list.append(job_id)
    if current_build_tag not in job_id_list:
        job_start_retry += 1
        print "Can't find the job status file after %s seconds" % str(DEFAULT_SLEEP_TIME * DEFAULT_JOB_START_TIMEOUT)
        if job_start_retry > DEFAULT_JOB_START_TIMEOUT:
            print "ERROR: job status is not created after %s seconds!" % str(DEFAULT_SLEEP_TIME * DEFAULT_JOB_START_TIMEOUT)
            sys.exit(1)
        time.sleep(DEFAULT_SLEEP_TIME)
    else:
        job_status_list = [os.path.splitext(status)[1].split(os.path.extsep)[1] for status in agent_status_file_list if os.path.splitext(status)[0] == current_build_tag]
        job_status_list.sort()
        if len(job_status_list) > 0:
            current_job_status = job_status_list[-1]
        else:
            current_job_status = None
        if current_job_status == DEFAULT_AGENT_JOB_STATUS['BEGIN']:
            if job_start_flag == 0:
                # init steps after job status is begin
                # print out current agent trigger configuration content
                print "INFO: current job [%s] status is [%s], status chain [%s]" % (current_build_tag, current_job_status, job_status_list)
                with open(agent_trigger_conf_fp) as fh:
                    conf = json.load(fh)
                    for key, value in conf.items():
                        print key + ": " + value

                # move agent trigger configuration json file to backup folder
                if os.path.exists(jenkins_conf_path):
                    os.remove(jenkins_conf_path)
                if os.path.exists(agent_trigger_conf_fp):
                    print "INFO: agent trigger configuration json file [%s] is backup to [%s]" % (agent_trigger_conf_fp, jenkins_conf_path)
                    shutil.copy(agent_trigger_conf_fp, jenkins_conf_path)
                else:
                    print "ERROR: agent trigger configuration file is missing before backup"
                job_start_flag = 1

            # print out job.log
            job_log_current_lineno = printlog(job_log_full_path, job_log_current_lineno)

        elif current_job_status == DEFAULT_AGENT_JOB_STATUS['FINISH']:
            # print out job.log
            job_log_current_lineno = printlog(job_log_full_path, job_log_current_lineno)
            print "INFO: job [%s] finished!" % current_build_tag

            # move job.log to backup folder
            if os.path.exists(jenkins_job_log_path):
                os.remove(jenkins_job_log_path)
            if os.path.exists(job_log_full_path):
                print "INFO: job log [%s] is moved to [%s]" % (job_log_full_path, jenkins_job_log_path)
                shutil.move(job_log_full_path, jenkins_job_log_path)
            break
        else:
            print "WARNING: job raise exception, the exception log is [%s]" % (current_build_tag + os.path.extsep + current_job_status)

            # print out job.log
            job_log_current_lineno = printlog(job_log_full_path, job_log_current_lineno)

        time.sleep(DEFAULT_SLEEP_TIME)
