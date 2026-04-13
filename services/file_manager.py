from configs.paths import data_path, job_output_excluded_extensions, job_output_excluded_files, MAX_OUTPUT_SIZE

import os
import zipfile

DATA_ROOT = os.path.realpath(data_path)

def is_within_root(path: str) -> bool:
    """
    Checks whether the given path is within the configured data root directory.

    Prevents path traversal outside of the allowed data dirrectory.
    """
    real_path = os.path.realpath(path)
    return os.path.commonpath([real_path, DATA_ROOT]) == DATA_ROOT

def get_files(extensions):
    """
    Recursively collect files from the configured data directory.

    Rules:
    - do not follow symlinked directories
    - do not include symlinked files
    - do not include files outside DATA_ROOT
    - optionally filter by file extensions

    Returns a sorted list of absolute file paths.
    """
    files = set()

    for current_root, _, filenames in os.walk(data_path, followlinks=True):
        for filename in filenames:
            file_path = os.path.join(current_root, filename)

            # # skip symlink files
            # if os.path.islink(file_path):
            #     continue

            if extensions and not any(filename.endswith(extension) for extension in extensions):
                continue

            # real_file_path = os.path.realpath(file_path)
            
            # if not is_within_root(file_path):
            #     continue

            files.add(file_path)

    return sorted(list(files))

def get_dirs() -> list[str]:
    """
    Recursively collect all directories from the configured data directory.

    Returns a sorted list of directory paths.
    """
    dirs = []

    for current_root, dirnames, _ in os.walk(data_path, followlinks=True):
        # safe_dirnames = []

        for dirname in dirnames:
            dir_path = os.path.join(current_root, dirname)

            # # skip symlink files
            # if os.path.islink(dir_path):
            #     continue

            # real_dir_path = os.path.realpath(dir_path)

            # if not is_within_root(real_dir_path):
            #     continue

            # safe_dirnames.append(dirname)
            dirs.append(dir_path)
        
        # dirnames[:] = safe_dirnames

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
            file_path = os.path.join(job_dir, file)

            # skip dirs
            if not os.path.isfile(file_path):
                continue

            # skip explicitly excluded files
            if file in job_output_excluded_files:
                continue

            # skip excluded files by extension
            if os.path.splitext(file)[1] in job_output_excluded_extensions:
                continue

            # add file to archive
            z.write(file_path, arcname=file)

def is_file_empty(file: str) -> bool:
    if not os.path.exists(file):
        return True

    if os.path.getsize(file) == 0:
        return True
    return False

def get_job_dir_size(job_dir: str) -> int:
    """
    Calculate total size of files in a job directory, excluding filtered files and directories.
    """
    total_size = 0
    
    for file in os.listdir(job_dir):
        file_path = os.path.join(job_dir, file)

        # skip dirs
        if not os.path.isfile(file_path):
            continue

        # skip explicitly excluded files
        if file in job_output_excluded_files:
            continue

        # skip excluded files by extension
        if os.path.splitext(file)[1] in job_output_excluded_extensions:
            continue

        total_size += os.path.getsize(file_path)
    
    return total_size

def is_output_too_big(output_dir: str) -> bool:
    """
    Check if total size of job output files exceeds the allowed limit.
    """
    return get_job_dir_size(output_dir) > MAX_OUTPUT_SIZE

def build_output_name(default_name: str, custom_name: str | None, extension: str|None) -> str:
    """
    Build output file name.

    Uses custom_name if provided, otherwise derives name from default_name.
    Ensures the given extension is applied (removes existing one if needed).
    """
    if custom_name and custom_name.strip():
        name = custom_name.strip()
    else:
        name = os.path.basename(default_name)

    if extension is not None:
        if name.endswith(extension):
            name = name[: -len(extension)]

        return f"{name}{extension}"
    
    return name