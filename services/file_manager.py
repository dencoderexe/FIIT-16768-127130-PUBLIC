import os

root_path: str = "/home/danilovd/data/"

def is_within_root(path: str) -> bool:
    real_path = os.path.realpath(path)
    return os.path.commonpath([real_path, root_path]) == root_path

def get_files(extensions):
    files = []

    for current_root, _, filenames in os.walk(root_path, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(current_root, filename)

            if extensions and not any(filename.endswith(extension) for extension in extensions):
                    continue

            files.append(file_path)

    return sorted(files)

def get_dirs() -> list[str]:
    dirs = []

    for current_root, dirnames, _ in os.walk(root_path, followlinks=True):
        for dirname in dirnames:
            dir_path = os.path.join(current_root, dirname)

            dirs.append(dir_path)

    return sorted(dirs)
