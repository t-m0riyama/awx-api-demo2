import random
import string


class DocIdUtils():

    def generate_id(n):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
