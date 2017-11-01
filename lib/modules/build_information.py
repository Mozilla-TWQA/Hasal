class BuildInformation(object):
    """
    This class refer to the method `generate_archive_perfherder_relational_table` of `lib.helper.generateBackfillTableHelper`
    """

    ARCHIVE_DATETIME = 'archive_datetime'
    ARCHIVE_URL = 'archive_url'
    ARCHIVE_DIR = 'archive_dir'
    PACKAGE_FILE_URL = 'pkg_fn_url'
    PACKAGE_JSON_URL = 'pkg_json_url'
    REVISION = 'revision'
    PERFHERDER_DATA = 'perfherder_data'

    def __init__(self, dict_obj):
        self.original_dict = dict_obj
        self.archive_datetime = dict_obj[self.ARCHIVE_DATETIME]
        self.archive_url = dict_obj[self.ARCHIVE_URL]
        self.archive_dir = dict_obj[self.ARCHIVE_DIR]
        self.package_file_url = dict_obj[self.PACKAGE_FILE_URL]
        self.package_json_url = dict_obj[self.PACKAGE_JSON_URL]
        self.revision = dict_obj[self.REVISION]
        self.perfherder_data = dict_obj.get(self.PERFHERDER_DATA, {})

        self._self_check()

    def _self_check(self):
        for field in [self.archive_datetime, self.archive_url, self.archive_dir, self.package_file_url, self.package_json_url, self.revision]:
            if field is None:
                raise Exception('Cannot create BuildInformation object from {}.'.format(self.original_dict))
