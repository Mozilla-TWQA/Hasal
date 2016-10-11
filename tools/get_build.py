"""

Usage:
  get_build.py <repo> <platform> [--user-email=<str>] [--build-hash=<str>] [--no-status-check]
  get_build.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --build-hash=<str>        Specify the build want to retrieve.
  --user-email=<str>        Specify the user email of build want to retrieve
  --no-status-check         Skip job status check
"""
import re
import urllib2
from thclient import TreeherderClient
from docopt import docopt


class GetBuild(object):
    ARCHIVE_URL = "https://archive.mozilla.org"
    NIGHTLY_LATEST_URL_FOLDER = "/pub/firefox/nightly/latest-mozilla-central/"
    PLATFORM_FN_MAPPING = {'linux32':{'key':'linux-i686','ext':'tar.bz2'},
                           'linux64':{'key':'linux-x86_64','ext':'tar.bz2'},
                           'mac':{'key':'mac','ext':'dmg'},
                           'win32':{'key':'win32','ext':'zip'},
                           'win64':{'key':'win64','ext':'zip'}}

    def __init__(self, user_email, status_check):
        self.project = 'try'
        self.platform_option = 'opt'
        self.resultsets = []
        self.user_email = user_email
        self.status_check = status_check
        self.thclient = TreeherderClient()

    def fetch_resultset(self, build_hash, default_count=500):
        tmp_resultsets = self.thclient.get_resultsets(self.project, count=default_count)
        for resultset in tmp_resultsets:
            if resultset['author'].lower() == self.user_email.lower():
                self.resultsets.append(resultset)
                if build_hash is None:
                    return resultset
                elif resultset['revision'] == build_hash:
                    return resultset
        print "Can't find the specify build hash [%s] in resultsets!!" % build_hash
        return None

    def get_job(self, resultset, platform):
        jobs = self.thclient.get_jobs('try', result_set_id=resultset['id'])
        for job in jobs:
            if job['platform_option'] == self.platform_option and job['platform'] == platform:
                return job
        print "Can't find the spcify platform and platform_options in jobs!!!" % (platform, self.platform_option)
        return None

    def get_build_link(self, platform, build_folder_url):
        response_obj = urllib2.urlopen(build_folder_url)
        if response_obj.getcode() == 200:
            for line in response_obj.readlines():
                match = re.search(r'(?<=href=").*?(?=")', line)
                if match:
                    href_link = match.group(0)
                    f_name = href_link.split("/")[-1]
                    if 'firefox' in f_name:
                        if platform.find("linux") >= 0:
                            if "linux" in f_name and ".tar.bz2" in f_name:
                                return href_link
                        elif platform.find("mac") >= 0:
                            if "mac" in f_name and ".dmg" in f_name:
                                return href_link
                        elif platform.find("win") >= 0:
                            if "win32.zip" in f_name:
                                return href_link
        return None

    def download_build(self, build_hash, platform):
        if platform[:3].lower() == "win":
            download_platform = "win32"
        else:
            download_platform = platform
        # generate url for build folder
        build_folder_url_template = "%s/pub/firefox/%s-builds/%s-%s/%s-%s/"
        build_folder_url = build_folder_url_template % (self.ARCHIVE_URL,
                                                        self.project, self.user_email, build_hash,
                                                        self.project, download_platform)
        print "Build folder url [%s]" % build_folder_url
        build_link = self.get_build_link(platform, build_folder_url)
        download_fn = build_link.split("/")[-1]
        download_link = self.ARCHIVE_URL + build_link
        print "Prepare to download the build from link [%s]" % download_link
        response = urllib2.urlopen(download_link)
        with open(download_fn, 'wb') as fh:
            fh.write(response.read())

    def get_build(self):
        pass


    def get_try(self, user_email, build_hash, platform):
        resultset = self.fetch_resultset(build_hash)
        if resultset:
            if build_hash is None:
                build_hash = resultset['revision']
            print "Resultset is found, and build hash is [%s]" % build_hash
            if self.status_check:
                job = self.get_job(resultset, platform)
                if job:
                    if job['result'].lower() == "success":
                        self.download_build(build_hash, platform)
                    else:
                        "Current job status is [%s] !!" % job['result'].lower()
                        return None
            else:
                self.download_build(build_hash, platform)

    def get_files_from_remote_url_folder(self, remote_url_str):
        pass

    def get_nightly(self, platform):
        remote_url_str = self.ARCHIVE_URL + self.NIGHTLY_LATEST_URL_FOLDER

        # get latest nightly build list from remote url folder
        remote_file_list = self.get_files_from_remote_url_folder(remote_url_str)

        # filter with platform, and return file name with extension
        if platform not in self.PLATFORM_FN_MAPPING:
            print "ERROR: we are currently not support the platform[%s] you specified!" % platform
        else:


        # combine file name with json

        # download files

        pass

def main():
    arguments = docopt(__doc__)
    get_build_obj = GetBuild(arguments['<user_email>'], arguments['--no-status-check'])
    get_build_obj.get_build(arguments['--build-hash'], arguments['<platform>'])

if __name__ == '__main__':
    main()
