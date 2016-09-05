"""

Usage:
  get_build.py <user_email> <platform> [--build-hash=<str>]
  get_build.py (-h | --help)

Options:
  -h --help                 Show this screen.
  --build-hash=<str>        Specify the build has want to retrieve.

"""
from thclient import TreeherderClient
from docopt import docopt

class GetBuild(object):

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

    def get_build_folder_url(self, build_hash, platform):
        build_folder_url_template = "https://archive.mozilla.org/pub/firefox/%s-builds/%s-%s/%s-%s/"
        resultset = self.fetch_resultset(build_hash)
        if resultset:
            job = self.get_build_status(resultset, platform)
            if job:
                if job['status'].lower() == "complete":
                    build_folder_url_str = build_folder_url_template % ()



def main():
    arguments = docopt(__doc__)
    get_build_obj = GetBuild(arguments['<user_email>'])
    get_build_obj.fetch_resultset(arguments['--build-hash'])


if __name__ == '__main__':
    main()
