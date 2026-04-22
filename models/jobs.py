from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict

from services.job_signal import bump_active_jobs_signal
from models.tools import Tool, Command

from configs.paths import jobs_path
from configs.tools import TOOLS

import os
import json
import uuid
import psutil
import logging
import threading
import subprocess

logger = logging.getLogger(__name__)

class Status(Enum):
    # job/step is currently running
    RUNNING = (
        "bi:arrow-repeat", 
        "yellow"
    )
    # job/step finished successfully
    SUCCESS = (
        "bi:check-circle-fill", 
        "green"
    )
    # job/step finished with the error or was terminated
    FAILED = (
        "bi:x-circle-fill", 
        "red"
    )
    # job/step has not started yet
    PENDING = (
        "bi:clock-history", 
        "gray"
    )

    def __init__(self, icon: str, color:str) -> None:
        self.icon = icon
        self.color = color

def datetime_to_str(dt) -> str|None:
    """
    Convert a datetime object to ISO string format.
    """
    return datetime.isoformat(dt) if dt else None

def datetime_from_str(dt_str) -> datetime|None:
    """
    Parse a datetime object from an ISO string.
    """
    return datetime.fromisoformat(dt_str) if dt_str else None

def memory_to_str(memory) -> str | None:
    """
    Convert memory size in bytes to a human-readable string.
    """
    if memory is None:
        return None

    for unit in ["B", "KiB", "MiB", "GiB"]:
        if memory < 1024:
            return f"{memory:.1f} {unit}"
        memory /= 1024

@dataclass
class Step:
    name: str
    status: Status

    # optional progress values for steps with measurable progress
    progress_current: Optional[int] = None
    progress_total: Optional[int] = None

    # timestamps for step lifecycle
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    def set_status(self, status: Status) -> None:
        """
        Update step status and related timestamps.
        """
        self.status = status
        if status in (Status.SUCCESS, Status.FAILED):
            self.finished_at = datetime.now()
        elif status == Status.RUNNING:
            self.started_at = datetime.now()

        bump_active_jobs_signal()
    
    def set_progress(self, progress: int) -> None:
        """
        Update current progress value for the step.
        """
        self.progress_current = progress
        bump_active_jobs_signal()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the step into a dictionary.
        """
        return {
            "name": self.name,
            "status": self.status.name,

            "progress_current": self.progress_current,
            "progress_total": self.progress_total,

            "started_at": datetime_to_str(self.started_at),
            "finished_at": datetime_to_str(self.finished_at),
        }

    @classmethod
    def from_dict(cls, data) -> "Step":
        """
        Create a Step instance from serialized data.
        """
        return cls(
            name=data["name"],
            status=Status[data["status"]],

            progress_current=data.get("progress_current"),
            progress_total=data.get("progress_total"),

            started_at=datetime_from_str(data.get("started_at")),
            finished_at=datetime_from_str(data.get("finished_at")),
        )
    
@dataclass
class Job:
    tool: Tool
    command: Command
    cmd: str
    args: Dict[str, object] = field(default_factory=dict)
    error_message: Optional[str] = ""

    # unique job identifier
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # runtime-only references (not serialized directly)
    thread: Optional[threading.Thread] = None
    process: Optional[subprocess.Popen] = None

    # job lifecycle timestamps
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    # memory usage tracking
    max_memory_usage: int | None = None
    current_memory_usage: int | None = None
    memory_usage_history: List[Dict[str, Any]] = field(default_factory=list)

    # cpu usage tracking
    _last_total_cpu_time: float | None = None
    _last_cpu_timestamp: datetime | None = None
    _cpu_times_by_pid: Dict[int, float] = field(default_factory=dict)

    current_cpu_usage: float | None = None
    max_cpu_usage: float | None = None
    cpu_usage_history: List[Dict[str, Any]] = field(default_factory=list)

    # runtime flags
    notified: bool = False
    terminated: bool = False

    status: Status = Status.PENDING
    steps: List[Step] = field(init=False)

    # paths related to the job
    job_dir: str = field(init=False)
    log_file: str = field(init=False)
    links: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Initialize derived fields and load memory history if available.
        """
        self.steps = [Step(step_name, Status.PENDING) for step_name in self.command.steps]
        self.job_dir = os.path.join(jobs_path, self.id)
        self.log_file = os.path.join(self.job_dir, f"{self.id}.log")

        try:
            path = os.path.join(self.job_dir, f"{self.id}.cpu.hist")
            if os.path.isfile(path):
                with open(path, "r") as file:
                    for line in file:
                        cpu, timestamp = line.strip().split(",")
                        self.cpu_usage_history.append({
                            "CPU": float(cpu),
                            "Timestamp": datetime.fromisoformat(timestamp),
                        })
        except Exception:
            logger.exception("[job:%s] Failed to load cpu usage history", self.id)

        try:
            path = os.path.join(self.job_dir, f"{self.id}.mem.hist")
            if os.path.isfile(path):
                with open(path, "r") as file:
                    for line in file:
                        memory, timestamp = line.strip().split(",")
                        self.memory_usage_history.append({
                            "Memory": int(memory),
                            "Timestamp": datetime.fromisoformat(timestamp),
                        })
        except Exception:
            logger.exception("[job:%s] Failed to load memory usage history", self.id)

    def set_status(self, status: Status) -> None:
        """
        Update job status and related timestamps.
        """
        self.status = status
        if status in (Status.SUCCESS, Status.FAILED):
            self.finished_at = datetime.now()
            if status == Status.FAILED:
                # mark any still-running steps as failed
                for step in self.steps:
                    if step.status == Status.RUNNING:
                        step.set_status(Status.FAILED)
        elif status == Status.RUNNING:
            self.started_at = datetime.now()
        bump_active_jobs_signal()

    def get_current_step(self) -> tuple[int, "Step"]|tuple[None, None]:
        """
        Return the currently running step, or the next pending one.
        """
        for i, step in enumerate(self.steps):
            if step.status == Status.RUNNING:
                return i, step
        for i, step in enumerate(self.steps):
            if step.status == Status.PENDING:
                return i, step
        return None, None
    
    def get_step_by_name(self, step_name) -> "Step"|None:
        """
        Find a step by its name.
        """
        for step in self.steps:
            if step.name == step_name:
                return step
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the job into a dictionary.
        """
        return {
            "id": self.id,

            "tool_key": self.tool.key,
            "command_key": self.command.key,
            "cmd": self.cmd,
            "args": self.args,
            "error_message": self.error_message,
            
            "started_at": datetime_to_str(self.started_at),
            "finished_at": datetime_to_str(self.finished_at),

            "max_cpu_usage": self.max_cpu_usage,
            "max_memory_usage": self.max_memory_usage,

            "status": self.status.name,
            "steps": [step.to_dict() for step in self.steps],

            "links": self.links,
        }
    
    @classmethod
    def from_dict(cls, data) -> "Job":
        """
        Create a Job instance from serialized data.
        """
        tool = TOOLS[data["tool_key"]]
        command = tool.commands[data["command_key"]]

        job = cls(
            id=data["id"],

            tool=tool,
            command=command,
            cmd=data["cmd"],
            args=data.get("args", {}),
            error_message=data.get("error_message", ""),

            started_at=datetime_from_str(data.get("started_at")),
            finished_at=datetime_from_str(data.get("finished_at")),

            max_cpu_usage=data.get("max_cpu_usage", 0),
            max_memory_usage=data.get("max_memory_usage", 0),

            notified=True,

            status=Status[data.get("status")],
        )
        job.links = data.get("links", [])
        job.steps = [Step.from_dict(item) for item in data.get("steps", [])]

        if not job.steps:
            # fallback for jobs serialized without explicit step data
            job.steps = [Step(step_name, job.status) for step_name in command.steps]

        return job
    
    def serialize(self) -> None:
        """
        Save job metadata and memory usage history to disk.
        """
        os.makedirs(self.job_dir, exist_ok=True)
        serialization_file = os.path.join(self.job_dir, f"{self.id}.json")
        try:
            with open(serialization_file, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("[job:%s] Failed to serialize job json", self.id)

        cpu_usage_history_file = os.path.join(self.job_dir, f"{self.id}.cpu.hist")
        try:
            with open(cpu_usage_history_file, "w") as file:
                for entry in self.cpu_usage_history:
                    file.write(f"{entry['CPU']},{entry['Timestamp'].isoformat()}\n")
        except Exception:
            logger.exception("[job:%s] Failed to serialize cpu usage history", self.id)

        memory_usage_history_file = os.path.join(self.job_dir, f"{self.id}.mem.hist")
        try:
            with open(memory_usage_history_file, "w") as file:
                for entry in self.memory_usage_history:
                    file.write(f"{entry['Memory']},{entry['Timestamp'].isoformat()}\n")
        except Exception as e:
            logger.exception("[job:%s] Failed to serialize memory usage history", self.id)

    @classmethod
    def deserialize(cls, path: str) -> "Job":
        """
        Load a serialized job from disk.
        """
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return cls.from_dict(data)
        except Exception:
            logger.exception("Failed to deserialize job from %s", path)
    
    def get_duration(self) -> str|None:
        """
        Return the job duration as a human-readable string.
        """
        if not self.started_at:
            return None
        
        end = self.finished_at or datetime.now()
        delta_seconds = int((end - self.started_at).total_seconds())

        if delta_seconds < 0:
            return None
        
        hours, remainder = divmod(delta_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
        
    def get_cpu_usage(self, append_last_recorded_cpu: bool = False) -> float | None:
        """
        Calculate and optionally record current CPU usage of the job process tree.

        CPU usage is estimated from accumulated user+system CPU time across the main
        process and all discovered child processes. Per-process CPU time is stored by PID
        so that finished child processes do not make the total accumulated CPU time drop.
        """
        now = datetime.now()

        if append_last_recorded_cpu and self.cpu_usage_history:
            self.cpu_usage_history.append({
                "CPU": self.cpu_usage_history[-1]["CPU"],
                "Timestamp": now,
            })
            return None

        if not self.process:
            return None

        # main process is a shell process, skip it
        try:
            proc = psutil.Process(self.process.pid)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            return None
        
        try:
            children = proc.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            return None

        # update last known accumulated cpu time for all currently visible processes
        for child in children:
            try:
                times = child.cpu_times()
                self._cpu_times_by_pid[child.pid] = times.user + times.system
            except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
                pass

        # keep cpu time from all processes (also finished)
        total_cpu_time = sum(self._cpu_times_by_pid.values())

        # first attempt
        if self._last_total_cpu_time is None or self._last_cpu_timestamp is None:
            self._last_total_cpu_time = total_cpu_time
            self._last_cpu_timestamp = now
            return None
        
        delta_cpu = total_cpu_time - self._last_total_cpu_time
        delta_time = (now - self._last_cpu_timestamp).total_seconds()

        self._last_total_cpu_time = total_cpu_time
        self._last_cpu_timestamp = now

        if delta_time <= 0:
            return None
        
        cpu = (delta_cpu / delta_time) * 100.0

        if cpu < 0:
            cpu = 0

        self.current_cpu_usage = cpu

        if self.max_cpu_usage is None or cpu > self.max_cpu_usage:
            self.max_cpu_usage = cpu

        self.cpu_usage_history.append({
            "CPU": cpu,
            "Timestamp": now,
        })

        return cpu

    def get_memory_usage(self, append_last_recorded_memory: bool = False) -> int | None:
        """
        Calculate and optionally record current memory usage of the job process group.
        """
        now = datetime.now()

        if append_last_recorded_memory and self.memory_usage_history:
            self.memory_usage_history.append({
                "Memory": self.memory_usage_history[-1]["Memory"],
                "Timestamp": now,
            })
            return None

        if not self.process:
            return None

        # main process is a shell process, skip it
        try:
            proc = psutil.Process(self.process.pid)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            return None

        memory = 0

        try:
            children = proc.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            return None

        # sum memory usage across all child processes spawned by the job
        for child in children:
            try:
                memory_info = child.memory_full_info()

                # PSS (Proportional Set Size) - most accurate:
                # shared memory is divided between processes
                if hasattr(memory_info, "pss"):
                    memory += memory_info.pss
                # fallback to USS (Unique Set Size):
                # counts only private (non-shared) memory
                elif hasattr(memory_info, "uss"):
                    memory += memory_info.uss
                # last fallback to RSS:
                # includes all shared memory, may overestimate usage
                else:
                    memory += memory_info.rss
            except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
                pass

        self.current_memory_usage = memory

        if self.max_memory_usage is None or self.current_memory_usage > self.max_memory_usage:
            self.max_memory_usage = memory

        self.memory_usage_history.append({
            "Memory": memory,
            "Timestamp": now,
        })

        return memory
    
    def get_mode(self) -> str:
        """
        Return a user-friendly description of analysis mode based on inputs.
        """
        args = self.args or {}

        tumor_sample = bool(args.get("tumor_bam"))
        normal_sample = bool(args.get("normal_bam"))

        if tumor_sample and normal_sample:
            return "Tumor-normal (paired)"
        elif tumor_sample:
            return "Tumor-only"
        else:
            return "-"
