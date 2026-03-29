from configs.paths import data_path

import os
import zipfile

def is_within_root(path: str) -> bool:
    real_path = os.path.realpath(path)
    return os.path.commonpath([real_path, data_path]) == data_path

def get_files(extensions):
    files = set()

    for current_root, _, filenames in os.walk(data_path, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(current_root, filename)

            if extensions and not any(filename.endswith(extension) for extension in extensions):
                    continue

            files.add(os.path.realpath(file_path))

    return sorted(list(files))

def get_dirs() -> list[str]:
    dirs = []

    for current_root, dirnames, _ in os.walk(data_path, followlinks=True):
        for dirname in dirnames:
            dir_path = os.path.join(current_root, dirname)

            dirs.append(dir_path)

    return sorted(dirs)

def write_zip(job_dir, bytes_io):
    excluded_files = ()
    excluded_extensions = {".log", ".json", ".hist",}
    
    with zipfile.ZipFile(bytes_io, "w", zipfile.ZIP_DEFLATED) as z:
        for file in os.listdir(job_dir):
            full_path = os.path.join(job_dir, file)

            if not os.path.isfile(full_path):
                continue

            if file in excluded_files:
                continue

            if os.path.splitext(file)[1] in excluded_extensions:
                continue

            z.write(full_path, arcname=file)
