from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import os
import re
import json
import uuid
import time
import shutil
import signal
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
    defaults: Dict[str, object] = field(default_factory=dict)
    optionals: Dict[str, str] = field(default_factory=dict)
    link_output_to_input_arg: Optional[str] = None

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
                defaults={
                    "coverage": 20,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                }
            )
        }
    ),
    "msisensor": Tool(
        key="msisensor",
        name="MSIsensor",
        description=(
            "MSIsensor is a C++ program to detect replication slippage variants at "
            "microsatellite regions, and differentiate them as somatic or germline. "
            "Given paired tumor and normal sequence data, it builds a distribution "
            "for expected (normal) and observed (tumor) lengths of repeated sequence "
            "per microsatellite, and compares them using Pearson's Chi-Squared Test. "
            "Comprehensive testing indicates MSIsensor is an efficient and effective "
            "tool for deriving microsatellite instability (MSI) status from standard "
            "tumor-normal paired sequence data."
        ),
        dir="/home/danilovd/tools/msisensor/", #TODO
        commands={
            "scan": Command(
                key="scan",
                name="scan",
                description="scan homopolymers and miscrosatelites",
                template=(
                    "./msisensor.linux scan "
                    "-d {reference_genome} "
                    "-o {output} "
                    "-l {min_homo_size} "
                    "-m {max_homo_size} "
                    "-c {context_len} "
                    "-s {max_microsat_len} "
                    "-r {min_microsat_rep} "
                    "-p {homopolymer_only} "
                ),
                steps=[
                    "Scanning reference genome"
                ],
                defaults={
                    "min_homo_size": 5,
                    "max_homo_size": 50,
                    "context_len": 5,
                    "max_microsat_len": 5,
                    "min_microsat_rep": 3,
                    "homopolymer_only": 0,
                },
                link_output_to_input_arg="reference_genome",
            ),
            "msi": Command(
                key="msi",
                name="msi",
                description="msi scoring",
                template=(
                    "./msisensor.linux msi "
                    "-d {microsatellite_list} "
                    "-n {normal_bam} "
                    "-t {tumor_bam} "
                    "-o {output} "

                    "-f {fdr_threshold} "
                    "-c {coverage} "
                    "-z {coverage_normalization} "
                    "-l {min_homo_size} "
                    "-p {min_homo_size_dist} "
                    "-m {max_homo_size_dist} "
                    "-q {min_microsat_size} "
                    "-s {min_microsat_size_dist} "
                    "-w {max_microsat_size_dist} "
                    "-u {span_size_window} "
                    "-b {threads} "
                    "-x {homopolymer_only} "
                    "-y {microsatellite_only} "
                ),
                steps=[
                    "Loading BED regions",
                    "Loading BAM files",
                    "Loading homopolymer and microsatellite sites",
                    "Preparing analysis windows",
                    "Computing homopolymer and microsatellite distributions",
                ],
                defaults={
                    "bed_file": None,
                    "fdr_threshold": 0.05,
                    "coverage": 20,
                    "coverage_normalization": 0,
                    "region": None,
                    "min_homo_size": 5,
                    "min_homo_size_dist": 10,
                    "max_homo_size_dist": 50,
                    "min_microsat_size": 3,
                    "min_microsat_size_dist": 5,
                    "max_microsat_size_dist": 40,
                    "span_size_window": 500,
                    "threads": 1,
                    "homopolymer_only": 0,
                    "microsatellite_only": 0,
                },
                optionals={
                    "bed_file": "-e",
                    "region": "-r",
                },
            ),
        }
    ),
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

def datetime_to_str(dt) -> str|None:
    return datetime.isoformat(dt) if dt else None

def datetime_from_str(dt_str) -> datetime|None:
    return datetime.fromisoformat(dt_str) if dt_str else None

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

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status.name,
            "progress_current": self.progress_current,
            "progress_total": self.progress_total,
            "finished_at": datetime_to_str(self.finished_at),
        }

    @classmethod
    def from_dict(cls, data) -> Step:
        return cls(
            name=data["name"],
            status=Status[data["status"]],
            progress_current=data.get("progress_current"),
            progress_total=data.get("progress_total"),
            finished_at=datetime_from_str(data.get("finished_at")),
        )

@dataclass
class Job:
    tool: Tool
    command: Command
    cmd: str
    args: Dict[str, object] = field(default_factory=dict)
    error_message: str = ""
    thread: Optional[threading.Thread] = None
    process: Optional[subprocess.Popen] = None

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    notified: bool = False
    terminated: bool = False

    status: Status = Status.PENDING

    steps: List[Step] = field(init=False)
    job_dir: str = field(init=False)
    log_file: str = field(init=False)
    hard_links: List[str] = field(default_factory=list)

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
    
    def to_dict(self):
        return {
            "id": self.id,
            "tool_key": self.tool.key,
            "command_key": self.command.key,
            "cmd": self.cmd,
            "args": self.args,
            "hard_links": self.hard_links,
            "error_message": self.error_message,
            "started_at": datetime_to_str(self.started_at),
            "finished_at": datetime_to_str(self.finished_at),
            "status": self.status.name,
            "steps": [step.to_dict() for step in self.steps],
        }
    
    @classmethod
    def from_dict(cls, data) -> Job:
        tool = TOOLS[data["tool_key"]]
        command = tool.commands[data["command_key"]]

        job = cls(
            id=data["id"],
            tool=tool,
            command=command,
            args=data.get("args", {}),
            cmd=data["cmd"],
            error_message=data.get("error_message", ""),
            started_at=datetime_from_str(data.get("started_at")),
            finished_at=datetime_from_str(data.get("finished_at")),
            status=Status[data.get("status")],
        )
        job.hard_links = data.get("hard_links", [])
        job.steps = [Step.from_dict(item) for item in data.get("steps", [])]

        if not job.steps:
            job.steps = [Step(step_name, job.status) for step_name in command.steps]

        return job
    
    def serialize(self):
        os.makedirs(self.job_dir, exist_ok=True)
        file = os.path.join(self.job_dir, f"{self.id}.json")
        with open(file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def deserialize(cls, path: str) -> Job:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls.from_dict(data)

jobs = []
jobs_lock = threading.Lock()

def get_jobs() -> List[Job]:
    with jobs_lock:
        return list(jobs)[::-1]
    
def get_saved_jobs():    
    if not os.path.isdir(jobs_path):
        return []
    
    saved_jobs = []

    for item in os.listdir(jobs_path):
        job_dir = os.path.join(jobs_path, item)

        if not os.path.isdir(job_dir):
            continue

        file = os.path.join(job_dir, f"{item}.json")
        if not os.path.isfile(file):
            continue

        try:
            job = Job.deserialize(file)
            saved_jobs.append(job)
        except Exception as e:
            print(f"Failed to load job from {file}: {e}")

    job_ids = {job.id for job in jobs}
    saved_jobs = [job for job in saved_jobs if job.id not in job_ids]

    saved_jobs.sort(
        key=lambda job: job.started_at,
        reverse=True
    )

    return saved_jobs
    
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
        elif job.command.key == "scan":
            if job.steps[0].status == Status.PENDING and "scanning chomosome" in line:
                _, step = job.get_current_step()            # Scanning reference genome
                if step is not None:
                    step.set_status(Status.RUNNING)
            elif "Total time consumed:" in line:
                _, step = job.get_current_step()            # Scanning reference genome
                if step is not None:
                    step.set_status(Status.SUCCESS)
            elif "fatal error:" in line or "failed" in line:
                _, step = job.get_current_step()
                job.error_message += line
                if step is not None:
                    step.set_status(Status.FAILED)          # Scanning reference genome
                job.set_status(Status.FAILED)
            elif job.status == Status.FAILED:
                job.error_message += line
            else:
                pass
        else:
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

def terminate_job_process(job: Job, timeout: float = 3.0):
    proc = job.process
    if proc is None:
        return

    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.1)

    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
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
                start_new_session=True,
            )
            job.process = proc

            job.started_at = datetime.now()
            job.set_status(Status.RUNNING)

            try:
                for line in proc.stdout:
                    if job.terminated:
                        terminate_job_process(job)
                        if "Job terminated by user.\n" not in job.error_message:
                            job.error_message += "Job terminated by user.\n"
                        break

                    log.write(line)
                    log.flush()

                    parse_job_output(job, line)

                if job.terminated and proc.poll() is None:
                    terminate_job_process(job)

                return_code = proc.wait()

            finally:
                if proc.stdout is not None:
                    proc.stdout.close()

        if job.terminated:
            _, current_step = job.get_current_step()
            if current_step is not None and current_step.status == Status.RUNNING:
                current_step.set_status(Status.FAILED)

            if job.status not in (Status.FAILED, Status.SUCCESS):
                job.set_status(Status.FAILED)

            if "Job terminated by user.\n" not in job.error_message:
                job.error_message += "Job terminated by user.\n"

        elif job.status not in (Status.FAILED, Status.SUCCESS):
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

        job.serialize()

    except Exception as e:
        job.error_message += f"{e}\n"
        _, current_step = job.get_current_step()
        if current_step is not None:
            current_step.set_status(Status.FAILED)
        job.set_status(Status.FAILED)

        try:
            job.serialize()
        except Exception:
            pass

    finally:
        job.process = None
        job.thread = None
        bump_signal()

def create_job(tool: Tool, command: Command, **kwargs):
    args = {**command.defaults, **kwargs}

    job = Job(
        tool=tool,
        command=command,
        cmd="",
        args=dict(args)
    )

    args["output"] = os.path.join(job.job_dir, args["output"])

    cmd = command.template.format(**args)

    for arg_name, flag in command.optionals.items():
        value = args.get(arg_name)
        if value is None or value == "":
            continue
        cmd += f"{flag} {value} "

    job.cmd = cmd

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

    for hardlink in job.hard_links:
        try:
            if os.path.exists(hardlink):
                os.remove(hardlink)
        except Exception as e:
            print(f"Failed to remove hardlink {hardlink}: {e}")

    bump_signal()

def get_job_by_id(job_id: str) -> Job|None:
    for job in jobs:
        if job.id == job_id:
            return job

    for job in get_saved_jobs():
        if job.id == job_id:
            return job

    return None

def cleanup_corrupted_jobs():
    if not os.path.isdir(jobs_path):
        return
    
    job_dirs = [
        dir for dir in os.listdir(jobs_path)
        if os.path.isdir(os.path.join(jobs_path, dir))
    ]

    for job_dir in job_dirs:
        job_dir_path = os.path.join(jobs_path, job_dir)
        json_path = os.path.join(job_dir_path, f"{job_dir}.json")
        log_path = os.path.join(job_dir_path, f"{job_dir}.log")

        if not os.path.isfile(json_path) or not os.path.isfile(log_path):
            shutil.rmtree(job_dir_path)

def create_output_hardlink(job: Job):
    input_arg = job.command.link_output_to_input_arg
    if not input_arg:
        return

    input_path = os.path.realpath(job.args.get(input_arg))
    output_path = os.path.join(job.job_dir, job.args.get("output"))

    if not input_path or not output_path:
        return

    if not os.path.isfile(input_path):
        return

    if not os.path.isfile(output_path):
        return

    input_dir = os.path.dirname(input_path)
    output_name = os.path.basename(output_path)
    link_path = os.path.join(input_dir, output_name)

    if os.path.abspath(link_path) == os.path.abspath(output_path):
        return

    if os.path.exists(link_path):
        return

    os.link(output_path, link_path)
    job.hard_links.append(link_path)