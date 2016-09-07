import os
import sys
import subprocess
from base import BaseProfiler


class MitmDumpProfiler(BaseProfiler):

    process = None

    def start_recording(self):
        if sys.platform == "linux2":
            default_dump_flow_cmd = ["mitmdump", "-w"]
        else:
            default_dump_flow_cmd = ["mitmdump", "--no-http2", "-w"]
        flow_file_fp = os.path.join(self.env.DEFAULT_FLOW_DIR, self.env.flow_file_fp)
        if not os.path.exists(self.env.DEFAULT_FLOW_DIR):
            os.makedirs(self.env.DEFAULT_FLOW_DIR)

        if not os.path.exists(flow_file_fp):
            # Will auto record the packet if the flow file is not exist
            default_dump_flow_cmd.append(flow_file_fp)
            if int(os.getenv("ENABLE_ADVANCE")) == 1:
                self.process = subprocess.Popen(default_dump_flow_cmd)
            else:
                prompt_str = "Can't find your flow file [%s], if you want to record your packet during this test, please type [Y|Yes] :"
                recording_prompt = raw_input(prompt_str)
                if len(recording_prompt) > 0 and recording_prompt[0].lower() == "y":
                    self.process = subprocess.Popen(default_dump_flow_cmd)
                else:
                    print "According to your answer, we will not record the packet during this test!"
        else:
            if sys.platform == "linux2":
                replay_cmd_list = ["mitmdump", "-S", flow_file_fp, "--no-pop", "--norefresh"]
            else:
                replay_cmd_list = ["mitmdump", "--no-http2", "-S", flow_file_fp, "--no-pop", "--norefresh"]
            self.process = subprocess.Popen(replay_cmd_list)

    def stop_recording(self, **kwargs):
        if sys.platform == "win32":
            subprocess.Popen("taskkill /IM mitmdump.exe /T /F", shell=True)
        else:
            self.process.send_signal(3)
