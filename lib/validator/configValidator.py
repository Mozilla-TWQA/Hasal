import os
import json
import jsonschema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(os.path.basename(__file__))


class ConfigValidator(object):
    CONFIG_ROOT = 'configs'
    CONFIG_EXT = '.json'
    SCHEMA_EXT = '.schema'

    @staticmethod
    def load_json_file(fp):
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
        if isinstance(dict_obj, str):
            dict_obj = ConfigValidator.load_json_file(dict_obj)
        if isinstance(schema_obj, str):
            schema_obj = ConfigValidator.load_json_file(schema_obj)

        try:
            jsonschema.validate(dict_obj, schema_obj)
            return True
        except Exception as e:
            logger.error(e)
            return False

    @staticmethod
    def get_all_configs_folder():
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
    def get_config_and_schema(config_folder):
        config_ret = []
        schema_ret = []

        root = config_folder
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
    def validate_all():
        all_config_folders = ConfigValidator.get_all_configs_folder()
        for c_folder in all_config_folders:
            logger.info('Validating Configs under {}'.format(os.path.relpath(c_folder)))
            config_list, schema_list = ConfigValidator.get_config_and_schema(c_folder)
            if len(config_list) > 0 and len(schema_list) > 0:

                for schema_path in schema_list:
                    logger.info('  Schema: {s}'.format(s=os.path.basename(schema_path)))
                    for config_path in config_list:
                        config_dict = ConfigValidator.load_json_file(config_path)
                        schema_dict = ConfigValidator.load_json_file(schema_path)
                        validate_result = ConfigValidator.validate(config_dict, schema_dict)
                        logger.info('    Config: {c} ... {r}'.format(c=os.path.basename(config_path),
                                                                     r='Pass' if validate_result else 'Failed'))


def main():
    ConfigValidator.validate_all()


if __name__ == '__main__':
    main()
