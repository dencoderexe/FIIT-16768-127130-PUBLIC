from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from datetime import datetime
import uuid
from services.job_signal import bump_signal

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

    def __init__(self, icon: str, color:str):
        self.icon = icon
        self.color = color

class Tool(Enum):
    MSISENSOR = (
        "MSIsensor", 
        (
            "MSIsensor is a C++ program to detect replication slippage variants at "
            "microsatellite regions, and differentiate them as somatic or germline. "
            "Given paired tumor and normal sequence data, it builds a distribution "
            "for expected (normal) and observed (tumor) lengths of repeated sequence "
            "per microsatellite, and compares them using Pearson's Chi-Squared Test. "
            "Comprehensive testing indicates MSIsensor is an efficient and effective "
            "tool for deriving microsatellite instability (MSI) status from standard "
            "tumor-normal paired sequence data."
        ),
        [
            "Step1",
            "Step2",
        ]
    )
    MSISENSOR_PRO = (
        "MSIsensor-pro", 
        (
            ""
        ),
        [

        ],
    )
    # MSISENSOR_2 = (
    #     "MSIsensor2", 
    #     (
    #         ""
    #     ),
    #     [

    #     ],
    # )
    # MANTIS = (
    #     "MANTIS", 
    #     (
    #         ""
    #     ),
    #     [

    #     ],
    # )
    # SAMTOOLS = (
    #     "Samtools", 
    #     (
    #         ""
    #     ),
    #     [

    #     ],
    # )

    def __init__(self, tool_name, tool_description, tool_steps: List[str]):
        self.tool_name = tool_name
        self.tool_description = tool_description
        self.tool_steps = tool_steps

@dataclass
class Step:
    name: str
    status: Status

@dataclass
class Job:
    tool: Tool
    command: str

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None

    status: Status = Status.PENDING

    steps: List[Step] = field(init=False)
    log_file: str = field(init=False)

    def __post_init__(self):
        self.steps = [Step(step_name, Status.PENDING) for step_name in self.tool.tool_steps]
        self.log_file = f"{self.id}.log"

    def set_status(self, status: Status):
        self.status = status
        if status in (Status.SUCCESS, Status.FAILED):
            self.finished_at = datetime.now()
        bump_signal()

    def set_step_status(self, step: Step, status: Status):
        for i in range(len(self.steps)):
            if self.steps[i].name == step.name:
                self.steps[i].status = status
        bump_signal()

jobs = []

def get_jobs() -> List[Job]:
    return jobs

def create_job():
    jobs.append(Job(Tool.MSISENSOR, "exec"))
    bump_signal()

# create_job()
# jobs[0].set_status(Status.RUNNING)
# jobs[0].set_step_status(jobs[0].steps[0], Status.SUCCESS)
# jobs[0].set_step_status(jobs[0].steps[1], Status.RUNNING)