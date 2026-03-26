from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict

from services.job_signal import bump_signal
from models.tools import Tool, Command

from configs.paths import jobs_path
from configs.tools import TOOLS

import os
import json
import uuid
import psutil
import threading
import subprocess

class Status(Enum):
    RUNNING = (
        "bi:arrow-repeat", 
        "yellow"
    )
    FAILED = (
        "bi:x-circle-fill", 
        "red"
    )
    SUCCESS = (
        "bi:check-circle-fill", 
        "green"
    )
    PENDING = (
        "bi:clock-history", 
        "gray"
    )

    def __init__(self, icon: str, color:str) -> None:
        self.icon = icon
        self.color = color

def datetime_to_str(dt) -> str|None:
    return datetime.isoformat(dt) if dt else None

def datetime_from_str(dt_str) -> datetime|None:
    return datetime.fromisoformat(dt_str) if dt_str else None

def memory_to_str(memory) -> str | None:
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

    progress_current: Optional[int] = None
    progress_total: Optional[int] = None

    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    def set_status(self, status: Status) -> None:
        self.status = status
        if status in (Status.SUCCESS, Status.FAILED):
            self.finished_at = datetime.now()
        elif status == Status.RUNNING:
            self.started_at = datetime.now()

        bump_signal()
    
    def set_progress(self, progress: int) -> None:
        self.progress_current = progress
        bump_signal()

    def to_dict(self) -> Dict[str, Any]:
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

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    thread: Optional[threading.Thread] = None
    process: Optional[subprocess.Popen] = None

    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    max_memory_usage: int = None
    current_memory_usage: int = None
    memory_usage_history: List[Dict[str, Any]] = field(default_factory=list)

    notified: bool = False
    terminated: bool = False

    status: Status = Status.PENDING
    steps: List[Step] = field(init=False)

    job_dir: str = field(init=False)
    log_file: str = field(init=False)
    links: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.steps = [Step(step_name, Status.PENDING) for step_name in self.command.steps]
        self.job_dir = os.path.join(jobs_path, self.id)
        self.log_file = os.path.join(self.job_dir, f"{self.id}.log")

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
            pass

    def set_status(self, status: Status) -> None:
        self.status = status
        if status in (Status.SUCCESS, Status.FAILED):
            self.finished_at = datetime.now()
            if status == Status.FAILED:
                for step in self.steps:
                    if step.status == Status.RUNNING:
                        step.set_status(Status.FAILED)
        elif status == Status.RUNNING:
            self.started_at = datetime.now()
        bump_signal()

    def get_current_step(self) -> tuple[int, "Step"]|tuple[None, None]:
        for i, step in enumerate(self.steps):
            if step.status == Status.RUNNING:
                return i, step
        for i, step in enumerate(self.steps):
            if step.status == Status.PENDING:
                return i, step
        return None, None
    
    def get_step_by_name(self, step_name) -> "Step"|None:
        for step in self.steps:
            if step.name == step_name:
                return step
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,

            "tool_key": self.tool.key,
            "command_key": self.command.key,
            "cmd": self.cmd,
            "args": self.args,
            "error_message": self.error_message,
            
            "started_at": datetime_to_str(self.started_at),
            "finished_at": datetime_to_str(self.finished_at),

            "max_memory_usage": self.max_memory_usage,

            "status": self.status.name,
            "steps": [step.to_dict() for step in self.steps],

            "links": self.links,
        }
    
    @classmethod
    def from_dict(cls, data) -> "Job":
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

            max_memory_usage=data.get("max_memory_usage", 0),

            status=Status[data.get("status")],
        )
        job.links = data.get("links", [])
        job.steps = [Step.from_dict(item) for item in data.get("steps", [])]

        if not job.steps:
            job.steps = [Step(step_name, job.status) for step_name in command.steps]

        return job
    
    def serialize(self) -> None:
        os.makedirs(self.job_dir, exist_ok=True)
        serialization_file = os.path.join(self.job_dir, f"{self.id}.json")
        with open(serialization_file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

        memory_usage_history_file = os.path.join(self.job_dir, f"{self.id}.mem.hist")
        try:
            with open(memory_usage_history_file, "w") as file:
                for entry in self.memory_usage_history:
                    file.write(f"{entry['Memory']},{entry['Timestamp'].isoformat()}\n")
        except Exception:
            pass

    @classmethod
    def deserialize(cls, path: str) -> "Job":
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.from_dict(data)
    
    def get_duration(self) -> str|None:
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

    def get_memory_usage(self, append_last_recorded_memory: bool = False) -> int | None:
        now = datetime.now()

        if append_last_recorded_memory and self.memory_usage_history:
            self.memory_usage_history.append({
                "Memory": self.memory_usage_history[-1]["Memory"],
                "Timestamp": now,
            })
            return None

        if not self.process:
            return None

        try:
            proc = psutil.Process(self.process.pid)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            return None

        memory = 0

        try:
            children = proc.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            return None

        for child in children:
            try:
                memory += child.memory_info().rss
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