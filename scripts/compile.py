import json
import os
from bundler import recursive_bundler, get_content


def compile_files():
    root = os.path.dirname(os.path.abspath(__file__))
    settings = json.loads(get_content(root+"\settings.json"))

    curr_dir = os.getcwd() + "\\"
    lines = recursive_bundler(curr_dir+settings["file_source"], curr_dir+settings["entry"], settings["exclude_modules"])

    with open(curr_dir+settings["target"],'w') as f:
        f.seek(0);
        f.writelines(lines[1:])
        f.close()
