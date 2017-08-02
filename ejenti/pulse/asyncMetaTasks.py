from baseMetaTasks import BaseMetaTask


class AsyncMetaTask(BaseMetaTask):

    def __init__(self, command_key, command_config, overwrite_cmd_configs=None):
        super(AsyncMetaTask, self).__init__(queue_type='async',
                                            command_key=command_key,
                                            command_config=command_config,
                                            overwrite_cmd_configs=overwrite_cmd_configs)
