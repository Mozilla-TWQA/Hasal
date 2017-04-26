import os
import glob
import time
import codecs
import shutil
import platform
import subprocess
import ConfigParser
import win32gui
import win32con
from ..common.commonUtil import CommonUtil
from ..common.logConfig import get_logger
from base import BaseProfiler

logger = get_logger(__name__)


class ObsProfiler(BaseProfiler):
    """
    Only support Windows 7 and Windows 10 currently.
    Please download "OBS-Studio-18.0.1-Full-Installer.exe" from https://github.com/jp9000/obs-studio/releases/tag/18.0.1 link,
    and then install into "C:\Program Files (x86)\" folder.

    Note: if there is error message "missing MSVCP120.dll",
    please download and install Visual C++ Redistributable Packages for Visual Studio 2013 from
    https://www.microsoft.com/en-us/download/details.aspx?id=40784
    """
    OBS_SETTINGS_DIR_PATH = r'C:\Users\user\AppData\Roaming\obs-studio'
    OBS_SETTINGS_FN = 'global.ini'

    OBS_COLLECTION_TEMPLATE_PATH = os.path.join(os.getcwd(), 'thirdparty', 'obsConfigs', 'collection')
    OBS_COLLECTION_DIR_PATH = r'C:\Users\user\AppData\Roaming\obs-studio\basic\scenes'
    OBS_COLLECTION_NAME = 'hasal'
    OBS_COLLECTION_FN = OBS_COLLECTION_NAME + '.json'

    OBS_PROFILE_TEMPLATE_PATH = os.path.join(os.getcwd(), 'thirdparty', 'obsConfigs', 'profile')
    OBS_PROFILE_DIR_PATH = r'C:\Users\user\AppData\Roaming\obs-studio\basic\profiles'
    OBS_32BIT_BIN_DIR_PATH = r'C:\Program Files (x86)\obs-studio\bin\32bit'
    OBS_32BIT_BIN_PATH = r'C:\Program Files (x86)\obs-studio\bin\32bit\obs32.exe'

    OBS_PROFILE_STREAM_ENCODER_FN = 'streamEncoder.json'
    OBS_PROFILE_BASIC_INI_FN = 'basic.ini'
    OBS_PROFILE_NAME = 'Hasal'
    OBS_RECORDING_FMT = 'mp4'
    OBS_VIDEO_OUTPUT_DIR_PATH = r'C:\Users\user\Videos\hasal'

    def __init__(self, input_env, input_index_config, input_browser_type=None, input_sikuli_obj=None):
        super(ObsProfiler, self).__init__(input_env, input_index_config, input_browser_type, input_sikuli_obj)
        self.process = None
        self.fh = None
        self.t1_time = None
        self.callback_ret = False
        self.video_recording_fps = self.input_index_config['video-recording-fps']
        self.obs_window_name = ['OBS', 'OBS Studio', 'obs32.exe', 'obs64.exe']
        self.exit_window_name = ['Exit OBS']

    def _get_obs_config_ini(self, filename):
        obs_config = ConfigParser.ConfigParser()
        with codecs.open(filename, 'r', encoding='utf-8-sig') as f:
            obs_config.readfp(f)
        logger.debug('Read Config: {}'.format(filename))
        return obs_config

    def _write_obs_config_ini(self, obs_config, filename):
        with open(filename, 'w') as f:
            obs_config.write(f)
            logger.debug('Write Config: {}'.format(filename))

    def _create_obs_profile_for_hasal(self, input_settings):
        # check local template, and OBS profile path
        if os.path.exists(ObsProfiler.OBS_PROFILE_TEMPLATE_PATH) and os.path.exists(ObsProfiler.OBS_PROFILE_DIR_PATH):
            # generate new profile folder
            new_profile_dp = os.path.join(ObsProfiler.OBS_PROFILE_DIR_PATH, ObsProfiler.OBS_PROFILE_NAME)
            if not os.path.exists(new_profile_dp):
                os.mkdir(new_profile_dp)
                logger.info('Create Profile Folder: {}'.format(new_profile_dp))

            # clean the video output folder
            if not os.path.exists(ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH):
                os.mkdir(ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH)
                logger.info('Create Video Output Folder: {}'.format(new_profile_dp))
            else:
                shutil.rmtree(ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH)
                os.mkdir(ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH)
                logger.info('Clean Video Output Folder: {}'.format(new_profile_dp))

            # prepare the streamEncoder.json
            stream_encoder_src_fp = os.path.join(ObsProfiler.OBS_PROFILE_TEMPLATE_PATH, ObsProfiler.OBS_PROFILE_STREAM_ENCODER_FN)
            stream_encoder_dst_fp = os.path.join(new_profile_dp, ObsProfiler.OBS_PROFILE_STREAM_ENCODER_FN)
            shutil.copy(stream_encoder_src_fp, stream_encoder_dst_fp)
            logger.info('Create Profile: {}'.format(stream_encoder_dst_fp))

            # prepare the profile basic.ini
            basic_ini_src_fp = os.path.join(ObsProfiler.OBS_PROFILE_TEMPLATE_PATH, ObsProfiler.OBS_PROFILE_BASIC_INI_FN)
            basic_ini_dst_fp = os.path.join(new_profile_dp, ObsProfiler.OBS_PROFILE_BASIC_INI_FN)
            profile_config = self._get_obs_config_ini(basic_ini_src_fp)
            for section in input_settings:
                for option in input_settings[section]:
                    profile_config.set(section, option, input_settings[section][option])
            self._write_obs_config_ini(profile_config, basic_ini_dst_fp)
            logger.info('Create Profile: {}'.format(basic_ini_dst_fp))
        else:
            raise Exception('Template OBS profile path or target obs profile path can\'t find!')

    def _create_obs_collection_for_hasal(self):
        # check local template, and OBS collection path
        if os.path.exists(ObsProfiler.OBS_COLLECTION_TEMPLATE_PATH) and os.path.exists(ObsProfiler.OBS_COLLECTION_DIR_PATH):
            # generate new collection folder
            collection_dst_fp = os.path.join(ObsProfiler.OBS_COLLECTION_DIR_PATH, ObsProfiler.OBS_COLLECTION_FN)
            if not os.path.exists(collection_dst_fp):
                # prepare the collection file
                collection_src_fp = os.path.join(ObsProfiler.OBS_COLLECTION_TEMPLATE_PATH, ObsProfiler.OBS_COLLECTION_FN)
                shutil.copy(collection_src_fp, collection_dst_fp)
                logger.info('Create Collection: {}'.format(collection_dst_fp))
            else:
                logger.info('Collection Exist: {}'.format(collection_dst_fp))

    def _modify_obs_global_settings(self):
        obs_global_fp = os.path.join(ObsProfiler.OBS_SETTINGS_DIR_PATH, ObsProfiler.OBS_SETTINGS_FN)
        if os.path.exists(ObsProfiler.OBS_SETTINGS_DIR_PATH) and os.path.exists(obs_global_fp):
            global_config = self._get_obs_config_ini(obs_global_fp)
            global_config.set('General', 'Language', 'en-US')

            # License Accepted
            try:
                is_licenseaccepted = global_config.get('General', 'LicenseAccepted')
            except:
                is_licenseaccepted = False
            if not is_licenseaccepted:
                logger.info('\n** Important **\n'
                            'When you use OBS to record the video for Hasal,'
                            ' you have to accept the OBS license before running cases.')
                raise Exception('Having to accept the OBS license agreement before running cases')

            # start OBS in system tray
            try:
                is_sys_tray = global_config.get('BasicWindow', 'SysTrayWhenStarted')
            except:
                is_sys_tray = False
            if is_sys_tray:
                logger.debug('SysTrayWhenStarted was True: {}'.format(obs_global_fp))
            else:
                global_config.set('BasicWindow', 'SysTrayWhenStarted', True)
                self._write_obs_config_ini(global_config, obs_global_fp)
                logger.info('Enable SysTrayWhenStarted: {}'.format(obs_global_fp))
        else:
            raise Exception('There is no OBS global settings file!')

    def _wait_obs_vidoe_file_creation(self):
        """
        After the OBS video file be created, then return. Max waiting time is 10 sec.
        :return: True after file was created. False when there is no file be created after 10 sec.
        """
        for _ in range(30):
            file_counter = len([item for item in os.listdir(ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH) if os.path.isfile(os.path.join(ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH, item))])
            if file_counter >= 1:
                time.sleep(0.1)
                return True
            time.sleep(0.1)
        return False

    def start_recording(self):
        if os.path.exists(self.env.video_output_fp):
            os.remove(self.env.video_output_fp)
        with open(self.env.recording_log_fp, 'w') as self.fh:
            if platform.system().lower() == "windows":
                # extract OBS profile to specify folder
                logger.info('OBS FPS: {}'.format(self.video_recording_fps))
                profile_settings_dict = {
                    'Video': {
                        'FPSInt': self.video_recording_fps,
                        'BaseCX': str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH),
                        'BaseCY': str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT),
                        'OutputCX': str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH),
                        'OutputCY': str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT)
                    },
                    'SimpleOutput': {
                        'RecFormat': ObsProfiler.OBS_RECORDING_FMT,
                        'FilePath': ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH
                    }
                }
                self._create_obs_profile_for_hasal(profile_settings_dict)
                # extract OBS collection to specify folder
                self._create_obs_collection_for_hasal()
                # modify OBS global settings
                self._modify_obs_global_settings()

                cmd_format = '{bin} --startrecording --profile {profile} --collection {collection}'
                cmd_str = cmd_format.format(bin=ObsProfiler.OBS_32BIT_BIN_PATH, profile=ObsProfiler.OBS_PROFILE_NAME, collection=ObsProfiler.OBS_COLLECTION_NAME)
                logger.debug('OBS Command: {}'.format(cmd_str))
                self.process = subprocess.Popen(cmd_str, cwd=ObsProfiler.OBS_32BIT_BIN_DIR_PATH, bufsize=-1, stdout=self.fh, stderr=self.fh)
                self._wait_obs_vidoe_file_creation()
            elif platform.system().lower() == "darwin":
                self.process = subprocess.Popen(["ffmpeg", "-f", "avfoundation", "-framerate", str(self.input_index_config['video-recording-fps']), "-video_size", str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT), "-i", CommonUtil.get_mac_os_display_channel(), "-filter:v", "crop=" + str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH) + ":" + str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT) + ":0:0", "-c:v", "libx264", "-r", str(self.input_index_config['video-recording-fps']), "-preset", "veryfast", "-g", "15", "-crf", "0", self.env.video_output_fp], bufsize=-1, stdout=self.fh, stderr=self.fh)
            else:
                self.process = subprocess.Popen(["ffmpeg", "-f", "x11grab", "-draw_mouse", "0", "-framerate", str(self.input_index_config['video-recording-fps']), "-video_size", str(self.env.DEFAULT_VIDEO_RECORDING_WIDTH) + "*" + str(self.env.DEFAULT_VIDEO_RECORDING_HEIGHT), "-i", CommonUtil.get_mac_os_display_channel(), "-c:v", "libx264", "-r", str(self.input_index_config['video-recording-fps']), "-preset", "veryfast", "-g", "15", "-crf", "0", self.env.video_output_fp], bufsize=-1, stdout=self.fh, stderr=self.fh)

    def stop_recording(self, **kwargs):
        if platform.system().lower() == "windows":
            # stop recording
            self.pywin32_ctrl_q()
            self.pywin32_return()
            time.sleep(2)

            # get latest video file for obs video output dir
            src_video_fp = max(glob.iglob(
                ObsProfiler.OBS_VIDEO_OUTPUT_DIR_PATH + os.sep + '*.' + ObsProfiler.OBS_RECORDING_FMT),
                key=os.path.getctime)
            print('Found Video file: {}'.format(src_video_fp))
            shutil.move(src_video_fp, self.env.video_output_fp)
        else:
            self.process.send_signal(3)

    def pywin32_ctrl_q_cb(self, hwnd, extra):
        window_title = win32gui.GetWindowText(hwnd)
        for name in self.obs_window_name:
            if name in window_title:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                self.callback_ret = True
                print('Found [{}] for closing.'.format(name))
                break

    def pywin32_ctrl_q(self):
        # try to move window after window launched
        for counter in range(50):
            win32gui.EnumWindows(self.pywin32_ctrl_q_cb, None)
            if self.callback_ret:
                self.callback_ret = None
                return True
            time.sleep(0.1)
        print('Cannot found one of [{}] for closing.'.format(self.obs_window_name))
        return False

    def pywin32_return_cb(self, hwnd, extra):
        window_title = win32gui.GetWindowText(hwnd)
        for name in self.exit_window_name:
            if name in window_title:
                win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN)
                self.callback_ret = True
                print('Found [{}] for press Enter.'.format(name))
                break

    def pywin32_return(self):
        # try to move window after window launched
        for counter in range(50):
            win32gui.EnumWindows(self.pywin32_return_cb, None)
            if self.callback_ret:
                self.callback_ret = None
                return True
            time.sleep(0.1)
        print('Cannot found one of [{}] for press Enter.'.format(self.obs_window_name))
        return False
