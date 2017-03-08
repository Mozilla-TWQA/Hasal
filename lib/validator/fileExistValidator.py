import os
from ..common.logConfig import get_logger
from baseValidator import BaseValidator

logger = get_logger(__name__)


class FileExistValidator(BaseValidator):

    def validate(self, input_validate_data):
        for fp in input_validate_data['check_fp_list']:
            if not os.path.exists(fp):
                return False
        return True
