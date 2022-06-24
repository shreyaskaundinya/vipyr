from json import loads
from bundler import get_content
import os
import time
from compile import compile_files


def get_mod_times(src):
    return [(t, os.path.getmtime(src+"\\"+t)) for t in os.listdir(src)]

def time_diff(prev, curr):
    if (len(prev) != len(curr)): return True

    for i in range(len(prev)):
        if prev[i][1] != curr[i][1]:
            return True
    return False

if __name__ == "__main__":
    cwd = os.getcwd()
    root = os.path.dirname(os.path.abspath(__file__))
    settings = loads(get_content(root+"\settings.json"))
    poll_time = int(settings["poll_time"])
    src = cwd+"\\"+settings["file_source"]

    prevTimes = get_mod_times(src)
    currTimes = []
    print("Watching files in : ", src)

    while True:
        time.sleep(poll_time)
        currTimes = get_mod_times(src)
        if (time_diff(prevTimes, currTimes)):
            print("See changes -> Compiling files...")
            compile_files()
        prevTimes = currTimes
        