import threading

_signal = 0
_lock = threading.Lock()

def get_signal():
    global _signal
    with _lock:
        return _signal

def bump_signal():
    global _signal
    with _lock:
        _signal += 1
        return _signal