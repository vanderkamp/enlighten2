import os
import shutil


def check_file(name, message=None):
    if not os.path.isfile(name):
        raise FileNotFoundError(message or "File " + name + " not found.")


def set_working_directory(working_directory):
    if os.path.exists(working_directory):
        shutil.rmtree(working_directory)
    os.makedirs(working_directory)
    os.chdir(working_directory)


def file_in_paths(filename, path_list):
    for path in path_list:
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            return full_path
    return None
