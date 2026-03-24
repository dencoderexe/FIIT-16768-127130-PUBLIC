from typing import List

from services.job_signal import bump_signal
from models.jobs import Status, Job
from models.tools import Tool, Command

from configs.paths import jobs_path

import os
import re
import time
import shutil
import signal
import threading
import subprocess

jobs = []
jobs_lock = threading.Lock()

def get_job_by_id(job_id: str) -> Job|None:
    for job in jobs:
        if job.id == job_id:
            return job

    for job in get_saved_jobs():
        if job.id == job_id:
            return job

    return None

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

    with jobs_lock:
        job_ids = {job.id for job in jobs}
    saved_jobs = [job for job in saved_jobs if job.id not in job_ids]

    saved_jobs.sort(
        key=lambda job: job.started_at,
        reverse=True
    )

    return saved_jobs
    
def parse_job_output(job: Job, line: str):
    if job.command.key == "scan":
        # Scanning reference genome for homopolymers and microsatellites
        if "Start at:" in line:
            job.steps[0].set_status(Status.RUNNING)
        elif "Total time consumed:" in line:
            job.steps[0].set_status(Status.SUCCESS)
            job.set_status(Status.SUCCESS)
        elif "fatal error:" in line or "failed" in line:
            _, step = job.get_current_step()
            job.error_message += line
            if step is not None:
                step.set_status(Status.FAILED)
            job.set_status(Status.FAILED)
        elif job.status == Status.FAILED:
            job.error_message += line
        return
    
    if job.tool.key == "samtools":
        _, step = job.get_current_step()
        if step is not None and step.status == Status.PENDING:
            step.set_status(Status.RUNNING)
        return
    
    if job.tool.key == "msisensor2" or job.tool.key == "msisensor-pro":
        if "Start at:" in line:
            job.get_step_by_name("Loading .BAM files").set_status(Status.RUNNING)
            job.get_step_by_name("Checking homopolymer and microsatellite file").set_status(Status.RUNNING)
        elif "loading homopolymer and microsatellite sites ..." in line:
            job.get_step_by_name("Checking .BAM files").set_status(Status.SUCCESS)
            job.get_step_by_name("Checking homopolymer and microsatellite file").set_status(Status.SUCCESS)

            job.get_step_by_name("Loading homopolymer and microsatellite sites").set_status(Status.RUNNING)
            job.get_step_by_name("Preparing analysis windows").set_status(Status.RUNNING)
        elif "Total loading windows:" in line:
            job.get_step_by_name("Preparing analysis windows").set_status(Status.SUCCESS)
            match = re.search(r"Total loading windows:\s+(\d+)", line)
            if match:
                job.get_step_by_name("Computing homopolymer and microsatellite distributions").progress_total = int(match.group(1))
                job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_progress(0)
        elif "Total loading homopolymer and microsatellites:" in line:
            job.get_step_by_name("Loading homopolymer and microsatellite sites").set_status(Status.SUCCESS)

            job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_status(Status.RUNNING)
        elif "Total time consumed:" in line:
            job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_status(Status.SUCCESS)
        elif "window:" in line:
            match = re.search(r"window:\s+(\d+)", line)
            if match:
                job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_progress(int(match.group(1)) + 1)
        elif "Program aborted:" in line or "fatal error:" in line:
            job.error_message += line
            job.set_status(Status.FAILED)
        elif job.status == Status.FAILED:
            job.error_message += line
        return
    
    if job.tool.key == "msisensor":
        if "Start at:" in line:
            job.get_step_by_name("Processing user defined region").set_status(Status.RUNNING)
        elif "loading bed regions ..." in line:
            job.get_step_by_name("Processing user defined region").set_status(Status.SUCCESS)

            job.get_step_by_name("Loading BED file").set_status(Status.RUNNING)
            job.get_step_by_name("Loading BAM files").set_status(Status.RUNNING)
            job.get_step_by_name("Checking homopolymer and microsatellite file").set_status(Status.RUNNING)
        elif "loading homopolymer and microsatellite sites ..." in line:
            job.get_step_by_name("Loading BED file").set_status(Status.SUCCESS)
            job.get_step_by_name("Loading BAM files").set_status(Status.SUCCESS)
            job.get_step_by_name("Checking homopolymer and microsatellite file").set_status(Status.SUCCESS)

            job.get_step_by_name("Loading homopolymer and microsatellite sites").set_status(Status.RUNNING)
            job.get_step_by_name("Preparing analysis windows").set_status(Status.RUNNING)
        elif "Total loading windows:" in line:
            job.get_step_by_name("Preparing analysis windows").set_status(Status.SUCCESS)
            match = re.search(r"Total loading windows:\s+(\d+)", line)
            if match:
                job.get_step_by_name("Computing homopolymer and microsatellite distributions").progress_total = int(match.group(1))
                job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_progress(0)
        elif "Total loading homopolymer and microsatellites:" in line:
            job.get_step_by_name("Loading homopolymer and microsatellite sites").set_status(Status.SUCCESS)

            job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_status(Status.RUNNING)
        elif "Total time consumed:" in line:
            job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_status(Status.SUCCESS)
        elif "window:" in line:
            match = re.search(r"window:\s+(\d+)", line)
            if match:
                job.get_step_by_name("Computing homopolymer and microsatellite distributions").set_progress(int(match.group(1)) + 1)
        elif "Program aborted:" in line or "fatal error:" in line:
            job.error_message += line
            job.set_status(Status.FAILED)
        elif job.status == Status.FAILED:
            job.error_message += line
        return
    
    if job.tool.key == "mantis":
        if "Getting repeat counts for repeat units (k-mers) ..." in line:
            job.get_step_by_name("Computing k-mer repeat counts").set_status(Status.RUNNING)
        elif "Filtering out outliers ..." in line:
            job.get_step_by_name("Computing k-mer repeat counts").set_status(Status.SUCCESS)

            job.get_step_by_name("Filtering outlier k-mer counts").set_status(Status.RUNNING)
        elif "Calculating instability scores ..." in line:
            job.get_step_by_name("Filtering outlier k-mer counts").set_status(Status.SUCCESS)

            job.get_step_by_name("Calculating instability scores").set_status(Status.RUNNING)
        elif "MANTIS complete." in line:
            job.get_step_by_name("Calculating instability scores").set_status(Status.SUCCESS)
            job.set_status(Status.SUCCESS)
        elif "Error" in line:
            job.error_message += line
            job.set_status(Status.FAILED)
        elif job.status == Status.FAILED:
            job.error_message += line
        return
    if job.tool.key == "repeatfinder":
        if job.get_step_by_name("Scanning reference genome for microsatellite regions").status == Status.PENDING:
            job.get_step_by_name("Scanning reference genome for microsatellite regions").set_status(Status.RUNNING)
        elif "ERROR:" in line:
            job.error_message += line
            job.set_status(Status.FAILED)
        elif job.status == Status.FAILED:
            job.error_message += line
        return
    # else:
    #     pass

def terminate_job_process(job: Job, timeout: float = 5.0):
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
            job.set_status(Status.RUNNING)
            job.steps[0].set_status(Status.RUNNING)

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

        if job.status == Status.SUCCESS:
            try:
                create_output_link(job)
            except Exception as e:
                job.error_message += f"Link creation failed: {e}\n"
        
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
        name=f"job-{job.id}",
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

    for link in job.links:
        try:
            if os.path.lexists(link):
                os.remove(link)
        except Exception as e:
            print(f"Failed to remove link {link}: {e}")

    bump_signal()

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

def create_output_link(job: Job):
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

    try:
        os.link(output_path, link_path)
        job.links.append(link_path)
        print(f"[hardlink] {link_path}")
        return
    except OSError as e:
        print(f"Hardlink failed: {e}")

    try:
        os.symlink(output_path, link_path)
        job.links.append(link_path)
        print(f"[symlink] {link_path}")
        return
    except OSError as e:
        print(f"Symlink failed: {e}")

def start_job_memory_monitor() -> None:
    def job_memory_monitor() -> None:
        while True:
            with jobs_lock:
                current_jobs = list(jobs)

            changed = False

            for job in current_jobs:
                if job.status != Status.RUNNING:
                    continue
                    
                job.get_memory_usage()
                changed = True

            if changed:
                bump_signal()
            time.sleep(1 if current_jobs else 3)
    
    thread = threading.Thread(
        target=job_memory_monitor,
        daemon=True,
        name="job-memory-monitor"
    )

    thread.start()
