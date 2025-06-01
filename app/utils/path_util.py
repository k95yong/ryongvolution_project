import os


def get_root_dir():
    cur_path = os.path.abspath(os.getcwd())
    while True:
        git_dir = os.path.join(cur_path, '.git')
        if os.path.isdir(git_dir):
            return cur_path
        parent_path = os.path.dirname(cur_path)
        if parent_path == cur_path:
            return None
        cur_path = parent_path
