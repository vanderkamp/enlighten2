from time import sleep
import os
import sys


def mdinfo_ready(mdinfo):
    with open(mdinfo, 'r') as f:
        return sum(1 for _ in f) > 4


def read_mdinfo(mdinfo):
    with open(mdinfo, 'r') as f:
        data = f.readlines()
    return int(data[1].split()[2]), data[-2].strip()[2:-1]


def get_steps(out):
    with open(out, 'r') as f:
        nstlim_line = [line for line in f if 'nstlim' in line][-1]
    return int(nstlim_line.split()[2][:-1])


def run_md_monitor(mdinfo, out):
    old_time_string = None

    while not os.path.exists(mdinfo) or not mdinfo_ready(mdinfo):
        sleep(1)

    steps = get_steps(out)
    while True:
        sleep(1)
        step, time_string = read_mdinfo(mdinfo)
        if time_string == old_time_string:
            continue
        if step == steps:
            break

        old_time_string = time_string
        print(time_string)
        sys.stdout.flush()
