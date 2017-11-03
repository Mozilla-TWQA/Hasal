import unittest
from ejenti.server_jobs.agents_file_name_list_handler import AgentsFileNameListHandler


class TestTasksTriggerMethods(unittest.TestCase):

    def test_get_file_name_list_from_object_list(self):
        """
        Ref data: https://www.backblaze.com/b2/docs/b2_list_file_names.html
        @return:
        """
        fake_data = [
            {
                "action": "upload",
                "contentLength": 6,
                "fileId": "4_z27c88f1d182b150646ff0b16_f1004ba650fe24e6b_d20150809_m012853_c100_v0009990_t0000",
                "fileName": "files/hello.txt",
                "size": 6,
                "uploadTimestamp": 1439083733000
            },
            {
                "action": "upload",
                "contentLength": 6,
                "fileId": "4_z27c88f1d182b150646ff0b16_f1004ba650fe24e6c_d20150809_m012854_c100_v0009990_t0000",
                "fileName": "files/world.txt",
                "size": 6,
                "uploadTimestamp": 1439083734000
            }
        ]
        expected_ret = ['files/hello.txt', 'files/world.txt']

        ret_list = AgentsFileNameListHandler._get_file_name_list_from_object_list(fake_data)
        self.assertEqual(expected_ret, ret_list)

    def test_get_agent_name_list_from_file_name_list(self):
        fake_data = [
            "file_name_list.json",
            "Askeing_recently.json",
            "mozilla-9527_history.json",
            "mozilla-9527_recently.json",
            "user-PC_history.json",
            "user-PC_recently.json",
            "Foo_PC_recently.json",
            "Bar_PC_history.json",
        ]
        expected_ret = [
            'Askeing',
            'mozilla-9527',
            'user-PC',
            'Foo_PC'
        ]

        ret_list = AgentsFileNameListHandler._get_agent_name_list_from_file_name_list(fake_data)
        self.assertEqual(expected_ret, ret_list)
