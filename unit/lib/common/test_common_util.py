import unittest

from lib.common.commonUtil import CommonUtil


class TestCommonUtil(unittest.TestCase):

    def _check_ref_data_for_mask_credential_value(self, ret_data, expected_mask_value='hidden_credential_value'):
        ret_username = ret_data.get('username')
        ret_password = ret_data.get('password')

        ret_bot_name = ret_data.get('FOO', {}).get('configs', {}).get('bot_name')
        ret_bot_api_token = ret_data.get('FOO', {}).get('configs', {}).get('bot_api_token')
        ret_bot_mgt_channel = ret_data.get('FOO', {}).get('configs', {}).get('bot_mgt_channel')
        ret_bot_election_channel = ret_data.get('FOO', {}).get('configs', {}).get('bot_election_channel')

        ret_b2_account_id = ret_data.get('BAR', {}).get('configs', {}).get('b2_account_id')
        ret_b2_account_id_ext = ret_data.get('BAR', {}).get('configs', {}).get('b2-account-id')
        ret_b2_account_key = ret_data.get('BAR', {}).get('configs', {}).get('b2_account_key')
        ret_b2_account_key_ext = ret_data.get('BAR', {}).get('configs', {}).get('b2-account-key')

        # Check the mask data
        expected_default_value = expected_mask_value
        for value in [ret_username, ret_password,
                      ret_bot_name, ret_bot_api_token, ret_bot_mgt_channel, ret_bot_election_channel,
                      ret_b2_account_id, ret_b2_account_id_ext, ret_b2_account_key, ret_b2_account_key,
                      ret_b2_account_key_ext]:
            self.assertEqual(value, expected_default_value)

        # Check the un-mask data
        ret_xxx = ret_data.get('BAR', {}).get('configs', {}).get('xxx')
        expected_xxx = 'XXX'
        self.assertEqual(ret_xxx, expected_xxx)

    def test_mask_credential_value(self):
        fake_data = {
            "username": "ERROR",
            "password": "ERROR",
            "FOO": {
                "module-path": "jobs.FOO",
                "trigger-type": "interval",
                "interval": 60,
                "max-instances": 1,
                "default-loaded": True,
                "configs": {
                    "bot_name": "ERROR",
                    "bot_api_token": "ERROR",
                    "bot_mgt_channel": "ERROR",
                    "bot_election_channel": "ERROR"
                }
            },
            "BAR": {
                "module-path": "jobs.BAR",
                "trigger-type": "interval",
                "interval": 10800,
                "max-instances": 1,
                "default-loaded": True,
                "configs": {
                    "alert_usage_percent": 80,
                    "b2_account_id": "ERROR",
                    "b2-account-id": "ERROR",
                    "b2_account_key": "ERROR",
                    "b2-account-key": "ERROR",
                    "xxx": 'XXX'
                }
            },
        }

        # Mask original data
        ret_data = CommonUtil.mask_credential_value(fake_data)
        self._check_ref_data_for_mask_credential_value(ret_data=ret_data)

        # Mask original data by specify mask symbol
        ret_data2 = CommonUtil.mask_credential_value(fake_data, input_mask_symbol='*')
        self._check_ref_data_for_mask_credential_value(ret_data=ret_data2, expected_mask_value='*')
