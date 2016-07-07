import time
import platform
import subprocess

if platform.system().lower() == "windows":
   import win32gui
   import win32con
elif platform.system().lower() == "darwin":
    from appscript import *


class WindowObject(object):
   DEFAULT_WMCTRL_CMD = "/usr/bin/wmctrl"

   def __init__(self, input_window_name):
       self.window_type = platform.system().lower()
       self.window_name = input_window_name
       self.get_window_identity()

   def get_window_identity(self):
       if self.window_type == "linux":
           self.window_identity = self.wmctrl_get_window_id()

   def pywin32_callback_func(self, hwnd, extra):
       rect = win32gui.GetWindowRect(hwnd)
       x = rect[0]
       y = rect[1]
       w = rect[2] - x
       h = rect[3] - y
       window_title = win32gui.GetWindowText(hwnd)
       if self.window_name in window_title:
           win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, self.pos_x, self.pos_y, self.window_width,
                                 self.window_height, 0)

   def pywin32_move_window(self):
       win32gui.EnumWindows(self.pywin32_callback_func, None)

   def wmctrl_get_window_id(self):
       window_list_cmd = self.DEFAULT_WMCTRL_CMD + " -l"
       for i in range(10):
           cmd_output = subprocess.check_output(window_list_cmd, shell=True)
           for tmp_line in cmd_output.splitlines():
               tmp_list = tmp_line.split(" ")
               window_title = " ".join(tmp_list[4:])
               if self.window_name in window_title:
                   return tmp_list[0]
           time.sleep(1)
       print "Can't find window name [%s] in wmctrl list!!!" % self.window_name
       return "0"

   def appscript_move_window(self):
       for app_ref in app('System Events').processes.file.get():
           if self.window_name in app_ref.name.get():
               application_obj = app(app_ref.name.get())
               application_obj.windows.bounds.set((self.pos_x, self.pos_y, self.window_width, self.window_height))

   def move_window_pos(self, pos_x, pos_y, window_height, window_width, window_gravity=0):
       self.pos_x = pos_x
       self.pos_y = pos_y
       self.window_height = window_height
       self.window_width = window_width
       self.window_gravity = window_gravity
       if self.window_type == "linux":
           self.wmctrl_move_window()
       elif self.window_type == "windows":
           self.pywin32_move_window()
       else:
           self.appscript_move_window()

   def wmctrl_move_window(self):
       mvarg_val = ",".join([str(self.window_gravity), str(self.pos_x), str(self.pos_y), str(self.window_width), str(self.window_height)])
       wmctrl_cmd = " ".join([self.DEFAULT_WMCTRL_CMD, "-i", "-r", self.window_identity, "-e", mvarg_val])
       print "Move windows command: [%s]" % wmctrl_cmd
       subprocess.call(wmctrl_cmd, shell=True)

