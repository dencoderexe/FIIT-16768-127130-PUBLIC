import threading

# internal counters used as change signals for active/finished jobs
_active_jobs_signal = 0
_finished_jobs_signal = 0

# lock to ensure thread-safe updates and reads
_signal_lock = threading.Lock()

def bump_active_jobs_signal():
    """
    increment active jobs signal (notify listeners)
    """
    global _active_jobs_signal
    with _signal_lock:
        _active_jobs_signal += 1

def bump_finished_jobs_signal():
    """
    increment finished jobs signal (notify listeners)
    """
    global _finished_jobs_signal
    with _signal_lock:
        _finished_jobs_signal += 1

def get_active_jobs_signal():
    """
    get current active jobs signal value
    """
    with _signal_lock:
        return _active_jobs_signal

def get_finished_jobs_signal():
    """
    get current finished jobs signal value
    """
    with _signal_lock:
        return _finished_jobs_signal