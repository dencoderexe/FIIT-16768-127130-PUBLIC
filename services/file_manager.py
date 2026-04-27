from configs.paths import data_path, job_output_excluded_extensions, job_output_excluded_files, MAX_OUTPUT_SIZE
from services.job_signal import bump_finished_jobs_signal

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
    # - do not follow symlinked directories
    # - do not include symlinked files
    # - do not include files outside DATA_ROOT
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

def get_dirs(extensions) -> list[str]:
    """
    Recursively collect all directories from the configured data directory.

    Rules:
    - do not follow symlinked directories
    - do not include symlinked directories
    - do not include directories outside DATA_ROOT
    - optionally filter by directory extensions (example: mkdir hg38.msisensor2.model)

    Returns a sorted list of directory paths.
    """
    dirs = []

    for current_root, dirnames, _ in os.walk(data_path, followlinks=False):
        safe_dirnames = []

        for dirname in dirnames:
            dir_path = os.path.join(current_root, dirname)

            # skip symlink dirs
            if os.path.islink(dir_path):
                continue

            real_dir_path = os.path.realpath(dir_path)

            # skip directories outside the allowed root
            if not is_within_root(real_dir_path):
                continue

            # keep directory for further traversal
            safe_dirnames.append(dirname)

            # optionally filter which directories are returned
            if extensions and not any(dirname.endswith(extension) for extension in extensions):
                continue

            dirs.append(dir_path)
        
        dirnames[:] = safe_dirnames

    return sorted(dirs)

def is_file_empty(file: str) -> bool:
    """
    Check whether a file is missing or empty.
    """
    if not os.path.exists(file):
        return True

    if os.path.getsize(file) == 0:
        return True
    return False

def get_job_archive_path(job_dir: str) -> str:
    """
    Return path to the job output archive.
    """
    return os.path.join(job_dir, "output.zip")

def get_job_archive(job_dir: str) -> str | None:
    """
    Return job output archive path if it exists.

    Returns None if the archive is not ready yet.
    """
    archive_path = get_job_archive_path(job_dir)

    if not os.path.exists(archive_path):
        return None

    return archive_path

def is_job_archive_too_big(job_dir: str) -> bool:
    """
    Check whether the existing job archive exceeds the maximum download size.

    Returns False if the archive does not exist yet.
    """
    archive_path = get_job_archive(job_dir)

    if archive_path is None:
        return False

    return os.path.getsize(archive_path) > MAX_OUTPUT_SIZE

def create_job_archive(job_dir: str) -> str:
    """
    Create a ZIP archive from job output files.

    Uses a temporary file and replaces the final archive only after successful writing.
    Excludes logs, metadata files, and configured file extensions.
    """
    archive_path = get_job_archive_path(job_dir)
    tmp_path = archive_path + ".tmp"

    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zip:
        for file in os.listdir(job_dir):
            file_path = os.path.join(job_dir, file)

            if not os.path.isfile(file_path):
                continue

            if file in job_output_excluded_files:
                continue

            if os.path.splitext(file)[1] in job_output_excluded_extensions:
                continue

            zip.write(file_path, arcname=file)

    os.replace(tmp_path, archive_path)
    bump_finished_jobs_signal()
    return archive_path

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