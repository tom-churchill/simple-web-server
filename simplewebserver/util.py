import random


def generate_random_hash():
    return hex(random.getrandbits(512)).split('x')[1]


# noinspection PyPep8Naming
class conditional_decorator(object):
    def __init__(self, decorator, condition):
        self.decorator = decorator
        self.condition = condition

    def __call__(self, func):
        if not self.condition:
            return func
        return self.decorator(func)


def format_bytes(num):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.0f %sB" % (num, unit)

        num /= 1024.0

    return "%.0f%sB" % (num, 'Y')


def get_path_parts(path, is_path_directory=None):
    split_path = path.split('/')

    if split_path[0] != '.':
        split_path.insert(0, '.')

    url = ''
    path_parts = []
    for i, name in enumerate(split_path):
        if name == '':
            continue

        is_directory = i != len(split_path) - 1

        if is_directory is True or is_path_directory is True:
            if name != '.':
                url += f'{name}/'

            name_url = f'/path/{url}'
            name = f'{name} /'
        else:
            url += f'{name}'
            name_url = f'/view-text/{url}'

        path_parts.append([name_url, name])

    return path_parts
