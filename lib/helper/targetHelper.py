from ..common.pyDriveUtil import PyDriveUtil


class TagetHelper(object):
    def __init__(self, env):
        self.drive_obj = PyDriveUtil()
        self.env = env

    def clean_target(self, file_name, target_folder=None):
        if target_folder is None:
            target_folder = self.env.DEFAULT_TEST_TARGET_FOLDER_URI
        self.drive_obj.update_file_content(target_folder, file_name, " ")

    def clone_target(self, file_id, new_title, target_folder=None):
        if target_folder is None:
            target_folder = self.env.DEFAULT_TEST_TARGET_FOLDER_URI
        result = self.drive_obj.copy_file(file_id, target_folder, new_title)
        url = result['alternateLink'].split("?")[0] + "?hl=en"
        id = result['id']
        return url, id

    def delete_target(self, file_id):
        self.drive_obj.delete_file(file_id)
