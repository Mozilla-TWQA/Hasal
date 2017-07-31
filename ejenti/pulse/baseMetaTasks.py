class BaseMetaTask(object):
    QUEUE_TYPE_SYNC = 'sync'
    QUEUE_TYPE_ASYNC = 'async'

    COMMAND_SETTINGS = 'cmd-settings'

    COMMAND_TASK_KEY_OBJECT = 'cmd_obj'
    COMMAND_TASK_KEY_PATTERN = 'cmd_pattern'
    COMMAND_TASK_KEY_INPUT_STR = 'input_cmd_str'

    def __init__(self, queue_type, command_key, command_config):
        """

        @param queue_type: the queue_type, 'sync' or 'async'.
        @param command_key: the specify command name. ex: 'download-latest-nightly'.
        @param command_config: the dict object which contains the command config.
        """
        self.command_key = command_key

        if queue_type == self.QUEUE_TYPE_SYNC or queue_type == self.QUEUE_TYPE_ASYNC:
            self.queue_type = queue_type
        else:
            raise Exception('Can not support this task type: {}'.format(queue_type))

        self.command_config = command_config
        if not self.command_config:
            raise Exception('There is no command config.')
        elif self.COMMAND_SETTINGS not in self.command_config:
            raise Exception('The command config was failed.\n{}'.format(self.command_config))
        self.command_config_settings = self.command_config.get(self.COMMAND_SETTINGS)

    def _generate_task_template(self, obj, pattern, input_str=''):
        """
        Return the MetaTask dict base on template.
        @param obj: command dict object.
        @param pattern: command pattern (command name).
        @param input_str: not used (only for ejenti interactive mode).
        @return: the dict object.
        """
        task_template = {
            self.COMMAND_TASK_KEY_OBJECT: obj,
            self.COMMAND_TASK_KEY_PATTERN: pattern,
            self.COMMAND_TASK_KEY_INPUT_STR: input_str
        }
        return task_template

    def get_cmd(self):
        """
        Return the MetaTask dict object, base on specified command_key.
        The command_key should be defined in `ejenti` cmd_config.json file.
        @return: MetaTask dict object.
        """
        if self.command_key not in self.command_config_settings:
            print('[Error] Not support command: {}'.format(self.command_key))
            return None

        command_pattern = self.command_key
        command_object = self.command_config_settings.get(command_pattern)
        task_object = self._generate_task_template(obj=command_object,
                                                   pattern=command_pattern)
        return task_object
