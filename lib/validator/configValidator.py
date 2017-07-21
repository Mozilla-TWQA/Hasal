import os
import json
import jsonschema
from lib.common.logConfig import get_logger

logger = get_logger(__name__)


class ConfigValidator(object):
    """
    Config Validator.
    Base on JSON Schema.
    """
    CONFIG_ROOT = 'configs'
    CONFIG_EXT = '.json'
    SCHEMA_EXT = '.schema'

    @staticmethod
    def load_json_file(fp):
        """
        Loading the JSON file and return the dict object.
        @param fp: The path of JSON file.
        @return: The dict object of JSON file's content. If it cannot be parsed to dict, it will be {}.
        """
        if os.path.exists(fp):
            try:
                with open(fp) as fh:
                    json_obj = json.load(fh)
                return json_obj
            except Exception as e:
                print e
                return {}
        else:
            return {}

    @staticmethod
    def validate(dict_obj, schema_obj):
        """
        Validating the dict_obj base on schema_obj.
        @param dict_obj: the dict object which you want to validate.
        @param schema_obj: the JSON schema.
        @return: True or False.
        """
        if isinstance(dict_obj, str):
            dict_obj = ConfigValidator.load_json_file(dict_obj)
        if isinstance(schema_obj, str):
            schema_obj = ConfigValidator.load_json_file(schema_obj)

        try:
            jsonschema.validate(dict_obj, schema_obj)
            return True
        except Exception as e:
            logger.error('\n{line}\n{message}\n{line}'.format(message=e,
                                                              line='-' * 60))
            return False

    @staticmethod
    def get_all_sub_configs_folder():
        """
        Getting all sub-configs folder path list under default configs folder.
        ex:
          configs
          |- exec
          |- global
          |- index
          ... and so on
          will return ['PATH/TO/CONFIGS/configs/exec', ...]
        @return: all sub-configs folder path
        """
        ret = []

        root = ConfigValidator.CONFIG_ROOT
        logger.debug('### Starting parsing folders: {}'.format(os.path.relpath(root)))
        for item in os.listdir(root):
            item_path = os.path.abspath(os.path.join(root, item))
            if os.path.isdir(item_path):
                logger.debug(' => Found Config Folder: {}'.format(os.path.relpath(item_path)))
                ret.append(item_path)
        return ret

    @staticmethod
    def get_config_list(parsed_folder):
        """
        Getting the config files (*.json) under folder.
        @param parsed_folder: The folder you want to parse.
        @return: The config files (*.json) list.
        """
        ret = []

        root = parsed_folder
        logger.debug('### Starting parsing Config: {}'.format(os.path.relpath(root)))
        for item in os.listdir(root):
            item_path = os.path.abspath(os.path.join(root, item))
            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item_path)[1]
                if file_ext == ConfigValidator.CONFIG_EXT:
                    logger.debug(' => Found Config: {}'.format(os.path.relpath(item_path)))
                    ret.append(item_path)
        return ret

    @staticmethod
    def get_schema_list(parsed_folder):
        """
        Getting the schema files (*.schema) under folder.
        @param parsed_folder: The folder you want to parse.
        @return: The schema files (*.schema) list.
        """
        ret = []

        root = parsed_folder
        logger.debug('### Starting parsing Schema: {}'.format(os.path.relpath(root)))
        for item in os.listdir(root):
            item_path = os.path.abspath(os.path.join(root, item))
            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item_path)[1]
                if file_ext == ConfigValidator.SCHEMA_EXT:
                    logger.debug(' => Found Schema: {}'.format(os.path.relpath(item_path)))
                    ret.append(item_path)
        return ret

    @staticmethod
    def get_config_and_schema(parsed_folder):
        """
        Getting the config files (*.json) and schema files (*.schema) under folder.
        @param parsed_folder: The folder you want to parse.
        @return: The config files (*.json) and schema files (*.schema) list. (config_list, schema_list)
        """
        config_ret = []
        schema_ret = []

        root = parsed_folder
        logger.debug('### Starting parsing Config/Schema: {}'.format(os.path.relpath(root)))
        for item in os.listdir(root):
            item_path = os.path.abspath(os.path.join(root, item))
            if os.path.isfile(item_path):
                file_ext = os.path.splitext(item_path)[1]
                if file_ext == ConfigValidator.CONFIG_EXT:
                    logger.debug(' => Found Config: {}'.format(os.path.relpath(item_path)))
                    config_ret.append(item_path)
                elif file_ext == ConfigValidator.SCHEMA_EXT:
                    logger.debug(' => Found Schema: {}'.format(os.path.relpath(item_path)))
                    schema_ret.append(item_path)
        return config_ret, schema_ret

    @staticmethod
    def validate_default_configs():
        """
        Validating all default configs under default configs folder.
        @return: True or False.
        """
        final_result = True
        all_config_folders = ConfigValidator.get_all_sub_configs_folder()
        for c_folder in all_config_folders:
            logger.info('Validating Configs under {}'.format(os.path.relpath(c_folder)))
            config_list, schema_list = ConfigValidator.get_config_and_schema(c_folder)
            if len(config_list) > 0 and len(schema_list) > 0:

                for schema_path in schema_list:
                    logger.info('  Schema: {s}'.format(s=os.path.basename(schema_path)))
                    for config_path in config_list:
                        config_obj = ConfigValidator.load_json_file(config_path)
                        schema_obj = ConfigValidator.load_json_file(schema_path)
                        validate_result = ConfigValidator.validate(config_obj, schema_obj)
                        if validate_result:
                            logger.info('    Config: {c} ... {r}'.format(c=os.path.basename(config_path), r='Pass'))
                        else:
                            logger.error('    Config: {c} ... {r}'.format(c=os.path.relpath(config_path), r='Failed'))
                            msg = 'Config settings {c} does not pass the schema {s} validation.'.format(
                                c=os.path.relpath(config_path),
                                s=os.path.relpath(schema_path))
                            logger.error(msg)
                            final_result = False
        return final_result


def main():
    result = ConfigValidator.validate_default_configs()
    exit(0 if result else 1)


if __name__ == '__main__':
    main()
