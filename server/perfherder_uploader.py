import random
import string
from thclient import (TreeherderClient, TreeherderResultSetCollection,
                      TreeherderJobCollection)


class PerfherderUploader(object):
    def __init__(self, client_id, secret, os_name, platform, machine_arch, build_arch, protocol='http', host='local.treeherder.mozilla.org'):
        # Perfherder Information
        self.potocol = protocol
        self.host = host
        self.client_id = client_id
        self.secret = secret
        self.repo = 'mozilla-central'
        # Author
        self.name = 'Hasal Bot'
        self.email = 'hasal-dev@mozilla.com'
        self.author = '{} <{}>'.format(self.name, self.email)
        self.subject = 'Updata Hasal Result'
        # Platform Information
        self.os_name = os_name
        self.platform = platform
        self.machine_arch = machine_arch
        self.build_arch = build_arch

    @staticmethod
    def gen_guid(length=32):
        return ''.join(random.choice(string.letters + string.digits) for _ in xrange(length))

    def create_resultset_dataset(self, revision, timestamp):

        return [
            {
                # The top-most revision in the list of commits for a push.
                'revision': revision,
                'author': self.author,
                'push_timestamp': timestamp,
                'type': 'push',
                # a list of revisions associated with the resultset. There should
                # be at least one.
                'revisions': [
                    {
                        'comment': '{} - {}'.format(self.subject, timestamp),
                        'revision': revision,
                        'repository': self.repo,
                        'author': self.author
                    }
                ]
            }
        ]

    def create_resultset_collection(self, dataset):
        trsc = TreeherderResultSetCollection()
        for data in dataset:
            trs = trsc.get_resultset()

            trs.add_push_timestamp(data['push_timestamp'])
            trs.add_revision(data['revision'])
            trs.add_author(data['author'])
            # trs.add_type(data['type'])

            revisions = []
            for rev in data['revisions']:
                tr = trs.get_revision()
                tr.add_revision(rev['revision'])
                tr.add_author(rev['author'])
                tr.add_comment(rev['comment'])
                tr.add_repository(rev['repository'])
                revisions.append(tr)
            trs.add_revisions(revisions)
            trsc.add(trs)
        return trsc

    def create_job_dataset(self, revision, browser, timestamp, perf_data, link='', version='', repo_link='', video_links='', extra_info_obj={}):
        job_guid = PerfherderUploader.gen_guid(len(revision))

        if browser.lower() == 'firefox':
            job_symbol = 'f'
            job_name = 'Hasal on Firefox'
        elif browser.lower() == 'chrome':
            job_symbol = 'c'
            job_name = 'Hasal on Chrome'
        else:
            job_symbol = 'o'
            job_name = 'Hasal'

        job_details = [
            {
                'content_type': 'raw_html',
                'title': 'Browser',
                'value': browser
            },
            {
                'content_type': 'raw_html',
                'title': 'Revision',
                'value': revision
            },
            {
                'content_type': 'raw_html',
                'title': 'Platform',
                'value': self.platform
            },
            {
                'content_type': 'raw_html',
                'title': 'OS',
                'value': self.os_name
            }
        ]
        if link:
            job_details.append({
                'content_type': "link",
                'url': link,
                'value': 'Link',
                'title': 'Dashboard'
            })
        if version:
            job_details.append({
                'content_type': 'raw_html',
                'title': 'Version',
                'value': version
            })
        if repo_link:
            job_details.append({
                'content_type': 'link',
                'url': repo_link,
                'title': 'Repo',
                'value': 'Link'
            })
        for title, link in video_links.items():
            job_details.append({
                'content_type': 'link',
                'url': link,
                'title': title,
                'value': 'Video'
            })
        for title, text in extra_info_obj.items():
            job_details.append({
                'content_type': 'raw_html',
                'title': title,
                'value': text
            })

        return [
            {
                'project': 'mozilla-central',
                'revision': revision,
                'job': {
                    'job_guid': job_guid,
                    'product_name': 'hasal',
                    'reason': 'scheduler',
                    # TODO:What is `who` for?
                    'who': 'Hasal',
                    'desc': 'Hasal Regression',
                    'name': job_name,
                    # The symbol representing the job displayed in
                    # treeherder.allizom.org
                    'job_symbol': job_symbol,

                    # The symbol representing the job group in
                    # treeherder.allizom.org
                    'group_symbol': 'Hasal',
                    'group_name': 'Hasal Performance Test',

                    # TODO: get the real timing from the test runner
                    'submit_timestamp': timestamp,
                    'start_timestamp': timestamp,
                    'end_timestamp': timestamp,

                    'state': 'completed',
                    'result': 'success',

                    'machine': 'local-machine',
                    # TODO: read platform test result
                    'build_platform': {
                        'platform': self.platform,
                        'os_name': self.os_name,
                        'architecture': self.build_arch
                    },
                    'machine_platform': {
                        'platform': self.platform,
                        'os_name': self.os_name,
                        'architecture': self.machine_arch
                    },

                    'option_collection': {'opt': True},

                    # jobs can belong to different tiers
                    # setting the tier here will determine which tier the job
                    # belongs to.  However, if a job is set as Tier of 1, but
                    # belongs to the Tier 2 profile on the server, it will still
                    # be saved as Tier 2.
                    'tier': 1,

                    # the ``name`` of the log can be the default of "buildbot_text"
                    # however, you can use a custom name.  See below.
                    # TODO: point this to the log when we have them uploaded
                    'log_references': [
                        {
                            'url': 'TBD',
                            'name': 'test log'
                        }
                    ],
                    # The artifact can contain any kind of structured data
                    # associated with a test.
                    'artifacts': [
                        {
                            'type': 'json',
                            'name': 'performance_data',
                            'job_guid': job_guid,
                            'blob': perf_data
                        },
                        {
                            'type': 'json',
                            'name': 'Job Info',
                            'job_guid': job_guid,
                            'blob': {
                                'job_details': job_details
                            }
                        }
                    ],
                    # List of job guids that were coalesced to this job
                    'coalesced': []
                }
            }
        ]

    def create_job_collection(self, dataset):
        tjc = TreeherderJobCollection()

        for data in dataset:
            tj = tjc.get_job()

            tj.add_revision(data['revision'])
            tj.add_project(data['project'])
            tj.add_coalesced_guid(data['job']['coalesced'])
            tj.add_job_guid(data['job']['job_guid'])
            tj.add_job_name(data['job']['name'])
            tj.add_job_symbol(data['job']['job_symbol'])
            tj.add_group_name(data['job']['group_name'])
            tj.add_group_symbol(data['job']['group_symbol'])
            tj.add_description(data['job']['desc'])
            tj.add_product_name(data['job']['product_name'])
            tj.add_state(data['job']['state'])
            tj.add_result(data['job']['result'])
            tj.add_reason(data['job']['reason'])
            tj.add_who(data['job']['who'])
            tj.add_tier(data['job']['tier'])
            tj.add_submit_timestamp(data['job']['submit_timestamp'])
            tj.add_start_timestamp(data['job']['start_timestamp'])
            tj.add_end_timestamp(data['job']['end_timestamp'])
            tj.add_machine(data['job']['machine'])

            tj.add_build_info(
                data['job']['build_platform']['os_name'],
                data['job']['build_platform']['platform'],
                data['job']['build_platform']['architecture']
            )

            tj.add_machine_info(
                data['job']['machine_platform']['os_name'],
                data['job']['machine_platform']['platform'],
                data['job']['machine_platform']['architecture']
            )

            tj.add_option_collection(data['job']['option_collection'])

            # data['artifact'] is a list of artifacts
            for artifact_data in data['job']['artifacts']:
                tj.add_artifact(
                    artifact_data['name'],
                    artifact_data['type'],
                    artifact_data['blob']
                )
            tjc.add(tj)
        return tjc

    def submit(self, revision, browser, timestamp, perf_data, link='', version='', repo_link='', video_links='', extra_info_obj={}):
        rs_dataset = self.create_resultset_dataset(revision=revision,
                                                   timestamp=timestamp)
        trsc = self.create_resultset_collection(rs_dataset)

        j_dataset = self.create_job_dataset(revision=revision,
                                            browser=browser,
                                            timestamp=timestamp,
                                            perf_data=perf_data,
                                            link=link,
                                            version=version,
                                            repo_link=repo_link,
                                            video_links=video_links,
                                            extra_info_obj=extra_info_obj)
        tjc = self.create_job_collection(j_dataset)

        client = TreeherderClient(protocol=self.potocol,
                                  host=self.host,
                                  client_id=self.client_id,
                                  secret=self.secret)
        client.post_collection(self.repo, trsc)
        client.post_collection(self.repo, tjc)
