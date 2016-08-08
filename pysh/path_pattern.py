import os
import re


def get_matching_paths(pattern):
    pattern = re.compile(pattern)
    for _dir_path, dir_names, file_names in os.walk('.'):
        for name in file_names:
            path = os.path.join(_dir_path, name)
            if pattern.match(path):
                yield path
