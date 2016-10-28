import os
import sys
import time
import json
import shutil


if "OUTPUTLOC" in os.environ and "HASAL_WORKSPACE" in os.environ and "WORKSPACE" in os.environ:
    full_path = os.environ["OUTPUTLOC"]
    conf_path = os.path.join(os.environ["HASAL_WORKSPACE"], "agent", "hasal.json")
    jenkins_conf_path = os.path.join(os.environ["WORKSPACE"], "hasal.json")
    jenkins_job_log_path = os.path.join(os.environ["WORKSPACE"], os.path.basename(os.environ["OUTPUTLOC"]))

    # clean archived files from former build
    if os.path.exists(jenkins_job_log_path):
        os.remove(jenkins_job_log_path)
    if os.path.exists(jenkins_conf_path):
        os.remove(jenkins_conf_path)
    time.sleep(10)  # wait for task begin and files generated
    begin_time = time.time()
    lines = 0
    copy_flag = False

    # wait for test started
    while True:
        if os.path.exists(full_path) and os.path.exists(conf_path):
            break
        time.sleep(1)
        check_time = time.time()
        if check_time - begin_time > 60:  # wait log file and json file generated for 1 minute
            print "Either %s or %s doesn't exist, raise exception!" % (full_path, conf_path)
            sys.exit(1)

    with open(conf_path) as fh:
        conf = json.load(fh)
        for key, value in conf.items():
            print key + ": " + value

    # wait for test finished
    while True:
        with open(full_path, "r") as f:
            current_file = f.readlines()
            current_lines = len(current_file)
            if current_lines > lines:
                for i in range(lines, current_lines):
                    print current_file[i].strip()
                lines = current_lines

        if not os.path.exists(conf_path):
            print "Detection of job finished."
            break
        elif not copy_flag and os.path.exists(conf_path):
                if os.path.exists(jenkins_conf_path):
                    os.remove(jenkins_conf_path)
                shutil.copy(conf_path, jenkins_conf_path)
                copy_flag = True
        else:
            time.sleep(2)

    # avoid race condition and loss log in jenkins
    with open(full_path, "r") as f:
        current_file = f.readlines()
        current_lines = len(current_file)
        if current_lines > lines:
            for i in range(lines, current_lines):
                print current_file[i].strip()
            lines = current_lines

    if os.path.exists(jenkins_job_log_path):
        os.remove(jenkins_job_log_path)
    shutil.move(full_path, jenkins_job_log_path)
    if os.path.exists(full_path):
        os.remove(full_path)
else:
    print "Cannot get environments 'OUTPUTLOC', 'HASAL_WORKSPACE', or 'WORKSPACE'"
    sys.exit(1)
