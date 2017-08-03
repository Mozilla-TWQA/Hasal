from baseMetaTasks import BaseMetaTask


class SyncMetaTask(BaseMetaTask):

    def __init__(self, command_key, command_config, overwrite_cmd_configs=None):
        super(SyncMetaTask, self).__init__(queue_type='sync',
                                           command_key=command_key,
                                           command_config=command_config,
                                           overwrite_cmd_configs=overwrite_cmd_configs)
