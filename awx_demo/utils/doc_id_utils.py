import random
import string

from awx_demo.utils.logging import Logging


class DocIdUtils():

    @Logging.func_logger
    def generate_id(n):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
