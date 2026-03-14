from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import os
import re
import uuid
import shutil
import threading
import subprocess

from services.job_signal import bump_signal

jobs_path = "/home/danilovd/jobs/"
tools_path = "/home/danilovd/tools/"

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

@dataclass(frozen=True)
class Command:
    key: str
    name: str
    description: str
    template: str
    steps: List[str] = field(default_factory=list)
    required: List[str] = field(default_factory=list)
    defaults: Dict[str, object] = field(default_factory=dict)

@dataclass(frozen=True)
class Tool:
    key: str
    name: str
    description: str
    dir: str
    commands: Dict[str, Command] = field(default_factory=dict)

TOOLS = {
    "msisensor2": Tool(
        key="msisensor2",
        name="MSIsensor2",
        description=(
            "MSIsensor2 is a novel algorithm based machine learning, featuring a large "
            "upgrade in the microsatellite instability (MSI) detection for tumor only "
            "sequencing data, including Cell-Free DNA (cfDNA), Formalin-Fixed "
            "Paraffin-Embedded(FFPE) and other sample types. The original MSIsensor is "
            "specially designed for tumor/normal paired sequencing data."
        ),
        dir="/home/danilovd/tools/msisensor2/", #TODO
        commands={
            "msi": Command(
                key="msi",
                name="msi",
                description="msi scoring",
                template=(
                    "./msisensor2 msi "
                    "-M {model} "
                    "-t {tumor_bam} "
                    "-o {output} "
                    "-c {coverage} "
                    "-b {threads} "
                    "-x {homopolymer_only} "
                    "-y {microsatellite_only} "
                ),
                steps=[
                    "Load .BAM files",
                    "Load homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                required=[
                    "model",
                    "tumor_bam",
                    "output",
                ],
                defaults={
                    "coverage": 20,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                }
            )
        }
    ),
    # "msisensor": Tool(
    #     key="msisensor",
    #     name="MSIsensor",
    #     description=(
    #         "MSIsensor is a C++ program to detect replication slippage variants at "
    #         "microsatellite regions, and differentiate them as somatic or germline. "
    #         "Given paired tumor and normal sequence data, it builds a distribution "
    #         "for expected (normal) and observed (tumor) lengths of repeated sequence "
    #         "per microsatellite, and compares them using Pearson's Chi-Squared Test. "
    #         "Comprehensive testing indicates MSIsensor is an efficient and effective "
    #         "tool for deriving microsatellite instability (MSI) status from standard "
    #         "tumor-normal paired sequence data."
    #     ),
    #     path="/home/danilovd/tools/msisensor/",#TODO
    #     commands={
    #         "scan": Command(
                
    #         ),
    #         "msi": Command(
    #             steps=[
    #                 "Loading BED regions",
    #                 "Loading BAM files",
    #                 "Loading homopolymer and microsatellite sites",
    #                 "Preparing analysis windows",
    #                 "Computing homopolymer and microsatellite distributions",
    #             ]
    #         ),
    #     }
    # ),
    # "msisensor-pro": Tool(
    #     key="msisensor-pro",
    #     name="MSIsensor-pro",
    #     description=(
    #         "MSIsensor-pro is an updated version of msisensor. MSIsensor-pro evaluates "
    #         "Microsatellite Instability (MSI) for cancer patients with next generation "
    #         "sequencing data. It accepts the whole genome sequencing, whole exome sequencing "
    #         "and target region (panel) sequencing data as input. MSIsensor-pro introduces a "
    #         "multinomial distribution model to quantify polymerase slippages for each tumor "
    #         "sample and a discriminative sites selection method to enable MSI detection "
    #         "without matched normal samples. For samples of various sequencing depths and "
    #         "tumor purities, MSIsensor-pro significantly outperformed the current leading "
    #         "methods which required matched normal samples in terms of both accuracy and "
    #         "computational cost."
    #     )
    # ),
    # "mantis": Tool(
    #     key="mantis",
    #     name="MANTIS",
    #     description=(
    #         "MANTIS (Microsatellite Analysis for Normal-Tumor InStability) is a program "
    #         "developed for detecting microsatellite instability from paired-end BAM files. "
    #         "To perform analysis, the program needs a tumor BAM and a matched normal BAM file "
    #         "(produced using the same pipeline) to determine the instability score between the "
    #         "two samples within the pair. Longer reads (ideally, 100 bp or longer) are recommended, "
    #         "as shorter reads are unlikely to entirely cover the microsatellite loci, and will be "
    #         "discarded after failing the quality control filters."
    #     )
    # ),
    # "samtools": Tool(
    #     key="samtools",
    #     name="Samtools",
    #     description=(
    #         "Samtools is a set of utilities that manipulate alignments in the SAM (Sequence Alignment/Map)"
    #         ", BAM, and CRAM formats. It converts between the formats, does sorting, merging and indexing, "
    #         "and can retrieve reads in any regions swiftly."
    #     )
    # ),
}

@dataclass
class Step:
    name: str
    status: Status
    progress_current: int = None
    progress_total: int = None
    finished_at: Optional[datetime] = None

    def set_status(self, status: Status):
        self.status = status
        if status in (Status.SUCCESS, Status.FAILED):
            self.finished_at = datetime.now()
        bump_signal()
    
    def set_progress(self, progress: int):
        self.progress_current = progress
        bump_signal()

@dataclass
class Job:
    tool: Tool
    command: Command
    cmd: str
    error_message: str = ""
    thread: Optional[threading.Thread] = None

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    notified: bool = False

    status: Status = Status.PENDING

    steps: List[Step] = field(init=False)
    job_dir: str = field(init=False)
    log_file: str = field(init=False)

    def __post_init__(self):
        self.steps = [Step(step_name, Status.PENDING) for step_name in self.command.steps]
        self.job_dir = os.path.join(jobs_path, self.id)
        self.log_file = os.path.join(self.job_dir, f"{self.id}.log")

    def set_status(self, status: Status):
        self.status = status
        if status in (Status.SUCCESS, Status.FAILED):
            self.finished_at = datetime.now()
            if status == Status.FAILED:
                for step in self.steps:
                    if step.status == Status.RUNNING:
                        step.set_status(Status.FAILED)
        bump_signal()

    def get_current_step(self):
        for i, step in enumerate(self.steps):
            if step.status == Status.RUNNING:
                return i, step
        for i, step in enumerate(self.steps):
            if step.status == Status.PENDING:
                return i, step
        return None, None

jobs = []
jobs_lock = threading.Lock()

def get_jobs() -> List[Job]:
    with jobs_lock:
        return list(jobs)
    
def parse_job_output(job: Job, line: str):
    if job.tool.key == "msisensor":
        if job.command.key == "msi":
            if "loading bed regions ..." in line:
                _, step = job.get_current_step()
                step.set_status(Status.RUNNING)             # Loading BED regions
            elif "loading homopolymer and microsatellite sites ..." in line:
                i, step = job.get_current_step()
                job.steps[i].set_status(Status.SUCCESS)     # Loading BED regions
                job.steps[i+1].set_status(Status.SUCCESS)   # Loading BAM files
                job.steps[i+2].set_status(Status.RUNNING)   # Loading homopolymer and microsatellite sites
            elif "Total loading windows:" in line:
                m = re.search(r"Total loading windows:\s+(\d+)", line)
                if m:
                    job.steps[-1].progress_total = int(m.group(1))
                    job.steps[-1].set_progress(0)
            elif "window:" in line:
                _, step = job.get_current_step()
                m = re.search(r"window:\s+(\d+)", line)
                if m:
                    step.set_progress(int(m.group(1)) + 1)
            elif "Total loading homopolymer and microsatellites:" in line:
                i, step = job.get_current_step()
                job.steps[i].set_status(Status.SUCCESS)     # Load homopolymer and microsatellite sites
                job.steps[i+1].set_status(Status.SUCCESS)   # Preparing analysis windows
                job.steps[i+2].set_status(Status.RUNNING)   # Computing homopolymer and microsatellite distributions
            elif "Total time consumed:" in line:
                _, step = job.get_current_step()
                step.set_status(Status.SUCCESS)             # Computing homopolymer and microsatellite distributions
                job.set_status(Status.SUCCESS)
            elif "Program aborted:" in line or "fatal error:" in line:
                _, step = job.get_current_step()
                job.error_message += line
                if step is not None:
                    step.set_status(Status.FAILED)
                job.set_status(Status.FAILED)
            elif job.status == Status.FAILED:
                job.error_message += line
            else:
                pass
        elif job.command.key == "scan": #TODO
            pass
    elif job.tool.key == "msisensor2":
        if job.command.key == "msi":
            if "loading homopolymer and microsatellite sites ..." in line:
                i, step = job.get_current_step()
                job.steps[i].set_status(Status.SUCCESS)   # Loading BAM files
                job.steps[i+1].set_status(Status.RUNNING)   # Loading homopolymer and microsatellite sites
            elif "Total loading windows:" in line:
                m = re.search(r"Total loading windows:\s+(\d+)", line)
                if m:
                    job.steps[-1].progress_total = int(m.group(1))
                    job.steps[-1].set_progress(0)
            elif "window:" in line:
                _, step = job.get_current_step()
                m = re.search(r"window:\s+(\d+)", line)
                if m:
                    step.set_progress(int(m.group(1)) + 1)
            elif "Total loading homopolymer and microsatellites:" in line:
                i, step = job.get_current_step()
                job.steps[i].set_status(Status.SUCCESS)     # Load homopolymer and microsatellite sites
                job.steps[i+1].set_status(Status.SUCCESS)   # Preparing analysis windows
                job.steps[i+2].set_status(Status.RUNNING)   # Computing homopolymer and microsatellite distributions
            elif "Total time consumed:" in line:
                _, step = job.get_current_step()
                step.set_status(Status.SUCCESS)             # Computing homopolymer and microsatellite distributions
                job.set_status(Status.SUCCESS)
            elif "Program aborted:" in line or "fatal error:" in line:
                _, step = job.get_current_step()
                job.error_message += line
                if step is not None:
                    step.set_status(Status.FAILED)
                job.set_status(Status.FAILED)
            elif job.status == Status.FAILED:
                job.error_message += line
            else:
                pass 
    elif job.tool.key == "msisensor-pro":
        pass
    elif job.tool.key == "mantis":
        pass
    elif job.tool.key == "samtools":
        pass
    else:
        pass

def run_job(job: Job):
    try:
        os.makedirs(job.job_dir, exist_ok=True)

        with open(job.log_file, "w", encoding="utf-8") as log:
            proc = subprocess.Popen(
                job.cmd,
                cwd=job.tool.dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            job.started_at = datetime.now()
            job.set_status(Status.RUNNING)

            for line in proc.stdout:
                log.write(line)
                log.flush()

                parse_job_output(job, line)

            return_code = proc.wait()

        if job.status not in (Status.FAILED, Status.SUCCESS):
            if return_code == 0:
                _, current_step = job.get_current_step()
                if current_step is not None:
                    current_step.set_status(Status.SUCCESS)
                job.set_status(Status.SUCCESS)
            else:
                job.error_message += f"\nExit code: {return_code}\n"
                _, current_step = job.get_current_step()
                if current_step is not None:
                    current_step.set_status(Status.FAILED)
                job.set_status(Status.FAILED)
    except Exception as e:
        job.error_message += f"{e}\n"
        _, current_step = job.get_current_step()
        if current_step is not None:
            current_step.set_status(Status.FAILED)
        job.set_status(Status.FAILED)
    finally:
        job.thread = None
        bump_signal()

def create_job(tool: Tool, command: Command, **kwargs):
    args = {**command.defaults, **kwargs}

    job = Job(
        tool=tool,
        command=command,
        cmd="",
    )

    args["output"] = os.path.join(job.job_dir, args["output"])

    job.cmd = command.template.format(**args)

    thread = threading.Thread(
        target=run_job, 
        args=(job,),
        daemon=False,
    )
    job.thread = thread

    with jobs_lock:
        jobs.append(job)

    thread.start()
    bump_signal()

def delete_job(job: Job):
    with jobs_lock:
        if job in jobs:
            jobs.remove(job)

    if job.job_dir and os.path.isdir(job.job_dir):
        if os.path.abspath(job.job_dir).startswith(os.path.abspath(jobs_path)):
            shutil.rmtree(job.job_dir)

    bump_signal()

def get_job(job_id: str) -> Job|None:
    for job in jobs:
        if job.id == job_id:
            return job

    return None

create_job(
    TOOLS["msisensor2"], 
    TOOLS["msisensor2"].commands["msi"], 
    model="models_hg38/",
    tumor_bam="/home/danilovd/data/L.1936.01/L.1936.01.T.bam",
    output="L.1936.01.T",
)

create_job(
    TOOLS["msisensor2"], 
    TOOLS["msisensor2"].commands["msi"], 
    model="models_b37_HumanG1Kv37",
    tumor_bam="/home/danilovd/data/L.1936.01/L.1936.01.T.bam",
    output="L.1936.01.T",
)