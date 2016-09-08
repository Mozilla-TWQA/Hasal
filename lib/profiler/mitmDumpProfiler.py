import os
import sys
import time
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

        if sys.platform == "linux2":
            subprocess.call(["gsettings", "set", "org.gnome.system.proxy",       "mode", "manual"])
            subprocess.call(["gsettings", "set", "org.gnome.system.proxy.http",  "host", "127.0.0.1"])
            subprocess.call(["gsettings", "set", "org.gnome.system.proxy.http",  "port", "8080"])
            subprocess.call(["gsettings", "set", "org.gnome.system.proxy.https", "host", "127.0.0.1"])
            subprocess.call(["gsettings", "set", "org.gnome.system.proxy.https", "port", "8080"])
        else:
            proxy_enable_cmd = ["reg", "add", "\"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\"", "/v", "ProxyEnable", "/t", "REG_DWORD", "/d", "1", "/f"]
            proxy_setting_cmd = ["reg", "add", "\"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\"", "/v", "ProxyServer", "/t", "REG_SZ", "/d", "127.0.0.1:8080", "/f"]
            os.system(" ".join(proxy_enable_cmd))
            os.system(" ".join(proxy_setting_cmd))
            os.system("cmd /c start \"\" /min \"C:\\Program Files\\Internet Explorer\\iexplore.exe\"")
            time.sleep(5)
            os.system("taskkill /T /IM iexplore.exe /F")

    def stop_recording(self, **kwargs):
        if sys.platform == "win32":
            subprocess.call(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"])
            subprocess.Popen("taskkill /IM mitmdump.exe /T /F", shell=True)
        else:
            self.process.send_signal(3)
            proxy_disable_cmd = ["reg", "add", "\"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\"", "/v", "ProxyEnable", "/t", "REG_DWORD", "/d", "0", "/f"]
            os.system(" ".join(proxy_disable_cmd))
