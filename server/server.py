import os
import web
import json
import time
from datetime import datetime
import shutil
import urlparse
from threading import Lock

from lib.common.outlier import outlier

urls = (
    '/', 'Index',
    '/reset/(.*)', 'Reset',
    '/hasal/(.*)/(.*)/(.*)', 'HasalServer',
    '/video_profile/(.*)/(.*)/(.*)', 'VideoProfileUpdater'
)


class Formater:

    @staticmethod
    def timestamp_to_date_string(timestamp):
        # For Javascript, 'var d = new Date(timestamp * 1000)' can work.
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


class StorageHandler:
    """
    Please add the 'config.json' file under '~/.hasal_server/'.
    The file content example:
        {"test_times": 30}
    If there is no config file, the default value will be 5 times.
    """
    def __init__(self):
        pass

    _storage_mutex = Lock()
    _storage_dir = os.path.expanduser('~/.hasal_server/')
    _storage_path = os.path.join(_storage_dir, 'dump.json')
    _config_path = os.path.join(_storage_dir, 'config.json')

    def load_config(self):
        """
        Return the config from config.json of '~/.hasal_server/'
        :return: The config json. ex: {"test_times": 30}
        """
        if os.path.isfile(self._config_path):
            with open(self._config_path, 'r') as f:
                return json.load(f)
        return {}

    def load(self):
        """
        Return the info from dump.json from '~/.hasal_server/'
        :return: json if file exists, or {}
        """
        if os.path.isfile(self._storage_path):
            with open(self._storage_path, 'r') as f:
                return json.load(f)
        return {}

    def save(self, json_obj):
        StorageHandler._storage_mutex.acquire()
        try:
            if os.path.isdir(self._storage_path):
                shutil.rmtree(self._storage_path)
            if not os.path.exists(self._storage_dir):
                os.makedirs(self._storage_dir)
            with open(self._storage_path, 'w') as f:
                json.dump(json_obj, f)
        finally:
            StorageHandler._storage_mutex.release()

    def remove(self):
        if os.path.isdir(self._storage_path):
            shutil.rmtree(self._storage_path)
        elif os.path.isfile(self._storage_path):
            os.remove(self._storage_path)


class HasalServer:
    """
    Hasal Server handler.
    """
    storage_handler = StorageHandler()
    storage = {}
    _calculator = outlier()
    _config = storage_handler.load_config()
    _config_test_times = _config.get('test_times', 5)
    _keys = ['os', 'target_browser', 'test', 'browser']
    _checks = ['os', 'target', 'test', 'browser', 'version', 'platform', 'value', 'video', 'comment']
    _count = 0
    _template = {
        'os': '',
        'target': '',
        'test': '',
        'browser': '',
        'version': '',
        'platform': '',
        'comment': '',
        'median_value': -1,
        'mean_value': -1,
        'sigma_value': -1,
        'origin_values': [],  # the list of (value, video, ip)
        'video_path': '',
        'profile_path': '',
        'timestamp': 0,
    }

    def __init__(self):
        HasalServer.storage = HasalServer.storage_handler.load()

    """
    def __del__(self):
        HasalServer._storage_handler.remove()
    """

    @staticmethod
    def check_input_json(json_obj):
        for item in HasalServer._checks:
            assert item in json_obj, 'The json should have "{}" value.'.format(item)

    @staticmethod
    def remove_tuple_from_values(list_obj, removed_values_list):
        tmp = list_obj[:]
        for v in removed_values_list:
            tmp = [item for item in tmp if tmp != v]
        return tmp

    @staticmethod
    def find_video_ip_by_median(list_obj, median):
        index = min([item[0] for item in list_obj], key=lambda x: abs(x - median))
        return [item for item in list_obj if index in item][0]

    @staticmethod
    def save_to_database(os, target, test, comment, json_obj):
        # TODO: store the json_obj under /os/target/test/comment/ path.
        pass

    @staticmethod
    def _generate_current_test_obj(json_obj, ip):
        info = HasalServer._template.copy()
        info['os'] = json_obj.get('os')
        info['target'] = json_obj.get('target')
        info['test'] = json_obj.get('test')
        info['browser'] = json_obj.get('browser')
        info['version'] = json_obj.get('version')
        info['platform'] = json_obj.get('platform')
        info['comment'] = json_obj.get('comment')
        info['origin_values'] = []  # TODO, add new value into it
        info['origin_values'].append([json_obj.get('value'), json_obj.get('video'), ip])
        return info

    @staticmethod
    def return_json(current_test_obj):
        HasalServer.storage_handler.save(HasalServer.storage)

        # TODO: we should remove this print method in the future.
        print(json.dumps(HasalServer.storage, indent=4))

        values_list = current_test_obj['origin_values']
        median_value = current_test_obj['median_value']
        mean_value = current_test_obj['mean_value']
        sigma_value = current_test_obj['sigma_value']
        timestamp = current_test_obj['timestamp']
        datestring = Formater.timestamp_to_date_string(timestamp) if timestamp else ''

        _, video, ip = HasalServer.find_video_ip_by_median(values_list, median_value)

        ret = {
            'median_value': median_value,
            'mean_value': mean_value,
            'sigma_value': sigma_value,
            'current_test_times': len(values_list),
            'video': video,
            'ip': ip,
            'config_test_times': HasalServer._config_test_times,
            'timestamp': timestamp,
            'date': datestring
        }
        return json.dumps(ret)

    def GET(self, os, target_browser, test):
        # TODO: this it for checking the result of Hasal Server.
        try:
            # check the url, server/hasal/<os>/<target_browser>/<test>
            assert os is not None and os != '', '[os] is empty.'
            assert target_browser is not None and target_browser != '', '[target_browser] is empty.'
            assert test is not None and test != '', '[test] is empty.'
            if os not in HasalServer.storage:
                return 'No os: {}'.format(os)
            elif target_browser not in HasalServer.storage[os]:
                return 'No target: {}'.format(target_browser)
            elif test not in HasalServer.storage[os][target_browser]:
                return 'No test: {}'.format(test)
            else:
                return json.dumps(HasalServer.storage[os][target_browser][test], indent=4)
        except AssertionError as e:
            raise web.badrequest(e.message)

    def POST(self, os, target_browser, test):
        """
        The input json example:
            json={
            "os": "mac",
            "target": "firefox-36.0.1",
            "test": "test_foo",
            "browser": "firefox",
            "version": "36.0.1",
            "platform": "x86_64",
            "value": 500,
            "video": "20160701_001.avi",
            "comment": "first test"
            }
        :param os: os. ex: 'linux'
        :param target_browser: target. ex: 'firefox 36'
        :param test: test name. ex: 'test_foo'
        :return: the json format string.
            ex: {
                "current_test_times": 3,
                "ip": "127.0.0.1",
                "mean_value": -1,
                "median_value": -1,
                "config_test_times": 5,
                "video": "20160701_001.avi",
                "sigma_value": -1
                }
        """
        try:
            # check the url, server/hasal/<os>/<target_browser>/<test>
            assert os is not None and os != '', '[os] is empty.'
            assert target_browser is not None and target_browser != '', '[target_browser] is empty.'
            assert test is not None and test != '', '[test] is empty.'

            # get the POST data
            ip = web.ctx.ip
            data = web.data()
            parameters = urlparse.parse_qs(data)
            # check the POST data contain 'json'
            assert 'json' in parameters, 'Can not get "json" parameter from POST data.'

            # check the input json object
            json_obj = json.loads(parameters['json'][0])
            HasalServer.check_input_json(json_obj)

            # add the os/target/test into storage
            if os not in HasalServer.storage:
                HasalServer.storage[os] = {}
            if target_browser not in HasalServer.storage[os]:
                HasalServer.storage[os][target_browser] = {}
            if test not in HasalServer.storage[os][target_browser]:
                HasalServer.storage[os][target_browser][test] = {}

            comment_name = json_obj.get('comment')
            # if there is /os/target/test/comment exists, then do following code
            if comment_name in HasalServer.storage[os][target_browser][test]:
                comment_obj = HasalServer.storage[os][target_browser][test][comment_name]

                browser_name = json_obj.get('browser')
                # if there is /os/target/test/comment/browser exists, then do following code
                if browser_name in comment_obj:
                    current_test_obj = comment_obj[browser_name]

                    # check the test times
                    values_list = current_test_obj['origin_values']
                    median_value = current_test_obj['median_value']

                    if median_value >= 0:
                        # already have median value, just return to the client
                        return HasalServer.return_json(current_test_obj)
                    else:
                        # add new value into values list
                        values_list.append([json_obj.get('value'), json_obj.get('video'), ip])
                        if len(values_list) >= HasalServer._config_test_times:
                            # more than 30 times, no median, cal the median and outliers
                            origin_seq = [item[0] for item in values_list]

                            # mean, median, sigma, seq, outliers = outlier().detect(seq)
                            mean, median, sigma, _, outliers = HasalServer._calculator.detect(origin_seq)
                            current_test_obj['origin_values'] = HasalServer.remove_tuple_from_values(values_list, outliers)
                            values_list = current_test_obj['origin_values']

                            if len(values_list) >= HasalServer._config_test_times:
                                # update the median, mean, and sigma
                                current_test_obj['median_value'] = median
                                current_test_obj['mean_value'] = mean
                                current_test_obj['sigma_value'] = sigma
                                # add timestamp
                                current_test_obj['timestamp'] = time.time()
                                # return the client
                                return HasalServer.return_json(current_test_obj)
                    # Keep going and return the client
                    return HasalServer.return_json(current_test_obj)
                # if no /os/target/test/comment/browser , then create browser obj.
                else:
                    current_test = HasalServer._generate_current_test_obj(json_obj, ip)
                    comment_obj[browser_name] = current_test
                    return HasalServer.return_json(current_test)
            # if there is no /os/target/test/comment , then create comment obj.
            else:
                # update the os/target/test result
                current_test = HasalServer._generate_current_test_obj(json_obj, ip)
                comment_obj = {
                    json_obj.get('browser'): current_test
                }
                HasalServer.storage[os][target_browser][test] = {
                    comment_name: comment_obj
                }
                return HasalServer.return_json(current_test)

        except AssertionError as e:
            raise web.badrequest(e.message)


class VideoProfileUpdater:
    """
    Update the video and profile to Hasal server storage.
    """
    _checks = ['os', 'target', 'test', 'browser', 'version', 'comment', 'video_path', 'profile_path']

    def __init__(self):
        HasalServer.storage = HasalServer.storage_handler.load()

    @staticmethod
    def check_input_json(json_obj):
        print('# check:')
        print(VideoProfileUpdater._checks)
        for item in VideoProfileUpdater._checks:
            assert item in json_obj, 'The json should have "{}" value.'.format(item)

    def POST(self, os, target_browser, test):
        """
        The input json example:
            json={
            "os": "mac",
            "target": "firefox-36.0.1",
            "test": "test_foo",
            "browser": "firefox",
            "version": "36.0.1",
            "comment": "first test",
            "video_path": "http://foo.bar/video",
            "profile_path": "http://foo.bar/profile"
            }
        :param os: os. ex: 'linux'
        :param target_browser: target. ex: 'firefox 36'
        :param test: test name. ex: 'test_foo'
        :return: OK with 200 code.
        """
        HasalServer.storage = HasalServer.storage_handler.load()
        try:
            # check the url, server/hasal/<os>/<target_browser>/<test>
            assert os is not None and os != '', '[os] is empty.'
            assert target_browser is not None and target_browser != '', '[target_browser] is empty.'
            assert test is not None and test != '', '[test] is empty.'

            # get the POST data
            ip = web.ctx.ip
            data = web.data()
            parameters = urlparse.parse_qs(data)
            # check the POST data contain 'json'
            assert 'json' in parameters, 'Can not get "json" parameter from POST data.'

            # check the input json object
            json_obj = json.loads(parameters['json'][0])
            VideoProfileUpdater.check_input_json(json_obj)

            comment_name = json_obj.get('comment')
            browser_name = json_obj.get('browser')

            # check the storage
            assert os in HasalServer.storage, \
                'No os [{}] in storage'.format(os)
            assert target_browser in HasalServer.storage[os], \
                'No target [{}] under os [{}]'.format(target_browser, os)
            assert test in HasalServer.storage[os][target_browser], \
                'No test [{}] under os [{}], target [{}]'.format(test, os, target_browser)
            assert comment_name in HasalServer.storage[os][target_browser][test], \
                'No comment [{}] under os [{}], target [{}], test [{}]'.format(comment_name, os, target_browser, test)
            assert browser_name in HasalServer.storage[os][target_browser][test][comment_name], \
                'No browser [{}] under os [{}], target [{}], test [{}], comment[{}]'.format(
                    browser_name, os, target_browser, test, comment_name)

            # Update Video and Profile
            HasalServer.storage[os][target_browser][test][comment_name][browser_name]['video_path'] = \
                json_obj.get('video_path', '')
            HasalServer.storage[os][target_browser][test][comment_name][browser_name]['profile_path'] = \
                json_obj.get('profile_path', '')
            # Save
            HasalServer.storage_handler.save(HasalServer.storage)

            return 'OK'
        except AssertionError as e:
            raise web.badrequest(e.message)


class Index:
    render = web.template.render('templates', base='layout')

    def GET(self):
        return self.render.readme()


class Reset:
    def GET(self, id):
        StorageHandler().remove()
        return 'Done.'


if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
