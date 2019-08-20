import os
import shutil
import subprocess


def check_file(name, message=None):
    if not os.path.isfile(name):
        raise FileNotFoundError(message or "File " + name + " not found.")


def dump_to_file(file, contents):
    with open(file, 'w') as f:
        f.write(contents)


def parse_template(template, params):
    with open(template) as f:
        return f.read().format(**params)


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


def merge_dicts_of_dicts(dict1, dict2):
    return {key: {**dict1.get(key, {}), **dict2.get(key, {})}
            for key in set(dict1.keys()) | set(dict2.keys())}


def run_in_shell(command, output):
    """
    Runs given command in the shell, redirecting both STDOUT and STDERR to
    the output file. Waits for the command to finish.
    """
    with open(output, 'w') as f:
        proc = subprocess.Popen(command, shell=True, stdout=f,
                                stderr=subprocess.STDOUT)
        proc.wait()


def run_at_path(path, command):
    cwd = os.getcwd()
    set_working_directory(path)
    exit_code = run(command)
    os.chdir(cwd)
    return exit_code


def run(command):
    out = open('out', 'w')
    err = open('err', 'w')
    try:
        subprocess.run(command.split(), stdout=out, stderr=err, check=True)
        exit_code = 0
    except subprocess.CalledProcessError as e:
        exit_code = e.returncode
    out.close()
    err.close()
    return exit_code
