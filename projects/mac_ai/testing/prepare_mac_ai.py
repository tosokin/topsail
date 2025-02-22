import os
import pathlib
import logging

from projects.core.library import env, config, run, configure_logging, export
from projects.matrix_benchmarking.library import visualize

import ollama, utils, remote_access, podman_machine

TESTING_THIS_DIR = pathlib.Path(__file__).absolute().parent
POD_VIRT_SECRET_PATH = pathlib.Path(os.environ.get("POD_VIRT_SECRET_PATH", "/env/POD_VIRT_SECRET_PATH/not_set"))


def prepare():
    base_work_dir = remote_access.prepare()
    prepare_llm_load_test(base_work_dir)

    ollama.prepare(base_work_dir)

    if config.project.get_config("prepare.podman.machine.enabled"):
        podman_machine.configure_and_start(base_work_dir)

    return 0


def prepare_llm_load_test(base_work_dir):
    # running this locally to know llm-load-test is configured in TOPSAIL's repo
    submodule_status = run.run("git submodule status | grep llm-load-test", capture_stdout=True).stdout
    submodule_commit = submodule_status.split()[0]
    submodule_path = submodule_status.split()[1]
    repo_url= run.run(f"git config --file=.gitmodules submodule.'{submodule_path}'.url", capture_stdout=True).stdout.strip()

    dest = base_work_dir / "llm-load-test"

    if dest.exists():
        logging.info(f"{dest} already exists, not cloning it.")
        return

    run.run_toolbox(
        "remote", "clone",
        repo_url=repo_url, dest=dest, version=submodule_commit,
    )
