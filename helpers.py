# -*- coding: UTF-8 -*-

import os

curr_dir = os.path.dirname(__file__)
def relative_path(path):
    return os.path.join(curr_dir, *path.split("/"))
