import argparse
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from argparse import ArgumentDefaultsHelpFormatter


class PyDriveUtil(object):

    def __init__(self):
        self.gauth = self.get_gauth()
        self.drive = GoogleDrive(self.gauth)

    def get_file_object(self, folder_uri, file_name):

        search_string = "'%s' in parents and trashed=false" % folder_uri
        file_list = self.drive.ListFile({'q': search_string}).GetList()
        for file_obj in file_list:
            if file_name in file_obj['title']:
                return file_obj
        return None

    def update_file_content(self, folder_uri, file_name, content):
        file_obj = self.get_file_object(folder_uri, file_name)
        file_obj.SetContentString(content)
        file_obj.Upload()

    def get_gauth(self):
        gauth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile("mycreds.txt")
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()

        # Initialize the saved creds
        gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile("mycreds.txt")
        return gauth

    def copy_file(self, file_id, folder_uri, new_title):
        return self.drive.auth.service.files().copy(fileId=file_id,
                                             body={"parents": [{"kind": "drive#fileLink", "id": folder_uri}],
                                                   'title': new_title}).execute()

    def delete_file(self, file_id):
        self.drive.auth.service.files().delete(fileId=file_id).execute()


def main():
    arg_parser = argparse.ArgumentParser(description='Pydrive util',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-u', action='store', dest='input_folder_uri', default=None,
                            help='Specify the uri path of folder.', required=True)
    arg_parser.add_argument('-f', action='store', dest='input_file_name', default=None,
                            help='Specify file name your want to update.', required=True)
    arg_parser.add_argument('-c', action='store', dest='input_content', default=None,
                            help='Specify content want to update.', required=True)
    args = arg_parser.parse_args()

    folder_uri = args.input_folder_uri
    file_name = args.input_file_name
    content = args.input_content

    pydrive_obj = PyDriveUtil()
    pydrive_obj.update_file_content(folder_uri, file_name, content)

if __name__ == '__main__':
    main()
