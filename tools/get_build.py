"""

Usage:
  get_build.py <user_email> <platform> [--build-hash=<str>]
  get_build.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --build-hash=<str>        Specify the build has want to retrieve.

"""
import re
import urllib2
from thclient import TreeherderClient
from docopt import docopt


class GetBuild(object):
    ARCHIVE_URL = "https://archive.mozilla.org"

    def __init__(self, user_email):
        self.project = 'try'
        self.platform_option = 'opt'
        self.resultsets = []
        self.user_email = user_email
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
                            if "win" in f_name and ".zip" in f_name:
                                return href_link
        return None

    def get_build(self, build_hash, platform):
        resultset = self.fetch_resultset(build_hash)
        if resultset:
            job = self.get_job(resultset, platform)
            if job:
                if job['result'].lower() == "success":
                    # generate url for build folder
                    build_folder_url_template = "%s/pub/firefox/%s-builds/%s-%s/%s-%s/"
                    build_folder_url = build_folder_url_template % (self.ARCHIVE_URL,
                                                                        self.project, self.user_email, build_hash,
                                                                        self.project, platform)
                    build_link = self.get_build_link(platform, build_folder_url)
                    download_fn = build_link.split("/")[-1]
                    download_link = self.ARCHIVE_URL + build_link
                    response = urllib2.urlopen(download_link)
                    with open(download_fn, 'wb') as fh:
                        fh.write(response.read())
                else:
                    "Current job status is [%s] !!" % job['result'].lower()
                    return None

def main():
    arguments = docopt(__doc__)
    get_build_obj = GetBuild(arguments['<user_email>'])
    get_build_obj.get_build(arguments['--build-hash'], arguments['<platform>'])

if __name__ == '__main__':
    main()
