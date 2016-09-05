__author__ = 'shako'
import os
import json
import subprocess


class HasalTask(object):

    configurations = {}
    cmd_parameter_keys = []

    def __init__(self, name, **kwargs):
        self.name = name
        if "path" in kwargs:
            self.src_conf_path = kwargs['path']
        self.read_configuration(**kwargs)

    def update(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
        self.read_configuration(**kwargs)

    def read_configuration(self, **kwargs):
        self.configurations = kwargs
        print self.configurations

    def update_svr_config(self):
        updated_key = ['svr_addr', 'svr_port', 'project_name']
        config_dict = {}
        for key in self.configurations:
            if key.lower() in updated_key:
                config_dict[key.lower()] = self.configurations[key]
        with open('svrConfig.json', 'w') as svrconfig_fh:
            json.dump(config_dict, svrconfig_fh)

    def generate_command_list(self):
        result_list = ['python', 'runtest.py', self.configurations['TYPE']]
        suite_fn = ".".join(['suite', self.configurations['TYPE'], self.configurations['SUITE']])
        if self.configurations['SUITE'] == "others":
            # Generate others suite file for this job
            with open(suite_fn, "w") as suite_fh:
                case_name_list = self.configurations['OTHERS'].split(",")
                for case_name in case_name_list:
                    if self.configurations['TYPE'] == 're':
                        case_full_name = ".".join(
                            ['tests', 'regression', case_name.split("_")[2], case_name])
                    else:
                        case_full_name = os.sep.join(['tests', 'pilot', case_name.split("_")[2], case_name])
                    suite_fh.write(case_full_name + os.linesep)
        else:
            # Generate suite file for selected web application
            if self.configurations['TYPE'] == 're':
                case_dir = os.path.join(os.getcwd(), 'tests', 'regression', self.configurations['SUITE'])
                with open(suite_fn, 'w') as suite_fh:
                    for f_name in os.listdir(case_dir):
                        if f_name.endswith(".py") and f_name != "__init__.py":
                            case_name = ".".join(['tests', 'regression', self.configurations['SUITE'], f_name.split(".")[0]])
                            suite_fh.write(case_name + os.linesep)
            else:
                case_dir = os.path.join(os.getcwd(), 'tests', 'pilot', self.configurations['SUITE'])
                with open(suite_fn, 'w') as suite_fh:
                    for f_name in os.listdir(case_dir):
                        if f_name.endswith(".sikuli"):
                            case_name = os.sep.join(['tests', 'pilot', self.configurations['SUITE'], f_name])
                            suite_fh.write(case_name + os.linesep)
        result_list.append(suite_fn)

        # Combine the parameter with cmd list
        for key in self.configurations:
            if key.startswith("--"):
                if self.configurations[key] == 'true':
                    result_list.append(key.lower())
                elif self.configurations[key] != 'false':
                    result_list.append(key.lower() + "=" + self.configurations[key])

        return result_list

    def run(self):
        print "run"
        cmd_list = self.generate_command_list()
        print " ".join(cmd_list)
        self.update_svr_config()
        with open("job.log", "w") as log_fh:
            p = subprocess.Popen(cmd_list, stdout=log_fh, stderr=log_fh, env=os.environ.copy())
            p.wait()
            log_fh.flush()
        os.remove(self.src_conf_path)

    def onstop(self):
        print "===== onstop ====="
        print self.src_conf_path
        print "===== onstop ====="
        if os.path.exists(self.src_conf_path):
            os.remove(self.src_conf_path)

    def teardown(self):
        print "===== teardown ====="
        print self.src_conf_path
        print "===== teardown ====="
        if os.path.exists(self.src_conf_path):
            os.remove(self.src_conf_path)
