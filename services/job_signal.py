import threading

_active_jobs_signal = 0
_finished_jobs_signal = 0
_signal_lock = threading.Lock()

def bump_active_jobs_signal():
    global _active_jobs_signal
    with _signal_lock:
        _active_jobs_signal += 1

def bump_finished_jobs_signal():
    global _finished_jobs_signal
    with _signal_lock:
        _finished_jobs_signal += 1

def get_active_jobs_signal():
    with _signal_lock:
        return _active_jobs_signal

def get_finished_jobs_signal():
    with _signal_lock:
        return _finished_jobs_signal