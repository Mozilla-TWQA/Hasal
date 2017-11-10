import unittest
from ejenti.server_jobs.agents_file_name_list_handler import AgentsFileNameListHandler


class TestTasksTriggerMethods(unittest.TestCase):

    def test_convert_gist_file_table_to_agent_list(self):
        """
        @return:
        """
        fake_data = {'Hasals-iMac.local_recently.json': {'url': 'https://api.github.com/gists/760a7061d0a2b3f7de81b7b8c88a3152', 'created_at': '2017-11-09T10:22:32Z', 'raw_url': 'https://gist.githubusercontent.com/mozhasalstatus/760a7061d0a2b3f7de81b7b8c88a3152/raw/fedc1e6ad19d82531b8b71e0b485d3c1ca826768/Hasals-iMac.local_recently.json', 'id': '760a7061d0a2b3f7de81b7b8c88a3152', 'updated_at': '2017-11-10T01:57:32Z'}, 'file_name_list.json': {'url': 'https://api.github.com/gists/cf4b97a3273e2f3117211a3663928133', 'created_at': '2017-11-10T03:54:49Z', 'raw_url': 'https://gist.githubusercontent.com/mozhasalstatus/cf4b97a3273e2f3117211a3663928133/raw/6c16abbcb96a9eda84e2208d3ed25b52d224a7dc/file_name_list.json', 'id': 'cf4b97a3273e2f3117211a3663928133', 'updated_at': '2017-11-10T03:58:49Z'},
                     'Hasals-iMac.local_history.json': {'url': 'https://api.github.com/gists/3d0a6d09c75e08fe6c361cd3422453d0', 'created_at': '2017-11-09T09:16:41Z', 'raw_url': 'https://gist.githubusercontent.com/mozhasalstatus/3d0a6d09c75e08fe6c361cd3422453d0/raw/e87ccd035808c8d37bd69a26713876cc37e72c76/Hasals-iMac.local_history.json', 'id': '3d0a6d09c75e08fe6c361cd3422453d0', 'updated_at': '2017-11-10T01:57:29Z'}}
        expected_ret = {"Hasals-iMac.local": {
            "recently": {
                "file_name": "Hasals-iMac.local_recently.json",
                "id": "760a7061d0a2b3f7de81b7b8c88a3152",
                "url": "https://api.github.com/gists/760a7061d0a2b3f7de81b7b8c88a3152",
                "raw_url": "https://gist.githubusercontent.com/mozhasalstatus/760a7061d0a2b3f7de81b7b8c88a3152/raw/Hasals-iMac.local_recently.json",
                "created_at": 1510194152,
                "updated_at": 1510250252
            },
            "history": {
                "file_name": "Hasals-iMac.local_history.json",
                "id": "3d0a6d09c75e08fe6c361cd3422453d0",
                "url": "https://api.github.com/gists/3d0a6d09c75e08fe6c361cd3422453d0",
                "raw_url": "https://gist.githubusercontent.com/mozhasalstatus/3d0a6d09c75e08fe6c361cd3422453d0/raw/Hasals-iMac.local_history.json",
                "created_at": 1510190201,
                "updated_at": 1510250249
            }
        }
        }

        ret_list = AgentsFileNameListHandler._convert_gist_file_table_to_agent_list(fake_data)
        self.assertEqual(expected_ret, ret_list, "expected_ret: {}\n ret_list: {}".format(expected_ret, ret_list))
