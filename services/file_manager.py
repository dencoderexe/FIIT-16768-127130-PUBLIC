from configs.paths import data_path, job_output_excluded_extensions, job_output_excluded_files

import os
import zipfile

def is_within_root(path: str) -> bool:
    """
    checks whether the given path is within the configured data root directory

    prevents path traversal outside of the allowed data dir
    """
    real_path = os.path.realpath(path)
    return os.path.commonpath([real_path, data_path]) == data_path

def get_files(extensions):
    """
    recursively collect files from the configured data directory

    optionally filters files by a list of exceptions

    returns a sorted list of absolute file paths
    """
    files = set()

    for current_root, _, filenames in os.walk(data_path, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(current_root, filename)

            if extensions and not any(filename.endswith(extension) for extension in extensions):
                continue

            files.add(os.path.realpath(file_path))

    return sorted(list(files))

def get_dirs() -> list[str]:
    """
    recursively collect all directories from the configured data directory

    returns a sorted list of directory paths
    """
    dirs = []

    for current_root, dirnames, _ in os.walk(data_path, followlinks=True):
        for dirname in dirnames:
            dir_path = os.path.join(current_root, dirname)

            dirs.append(dir_path)

    return sorted(dirs)

def write_zip(job_dir, bytes_io):
    """
    create a ZIP archive from files in a job directory:

    - includes only files (no subdirs)

    - exludes logs and metadata files by extension

    - writes archive into an in-memory buffer (bytes_io)
    """
    
    with zipfile.ZipFile(bytes_io, "w", zipfile.ZIP_DEFLATED) as z:
        for file in os.listdir(job_dir):
            full_path = os.path.join(job_dir, file)

            # skip dirs
            if not os.path.isfile(full_path):
                continue

            # skip explicitly excluded files
            if file in job_output_excluded_files:
                continue

            # skip excluded files by extension
            if os.path.splitext(file)[1] in job_output_excluded_extensions:
                continue

            # add file to archive
            z.write(full_path, arcname=file)
