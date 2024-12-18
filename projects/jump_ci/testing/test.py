#!/usr/bin/env python

import sys
import subprocess
import fire
import logging
logging.getLogger().setLevel(logging.INFO)


from projects.core.library import env, config, run, configure_logging
configure_logging()

from projects.jump_ci.testing import utils, prepare_jump_ci, tunnelling

def jump_ci(command):
    @utils.entrypoint()
    def do_jump_ci():
        """
        *Jump-CI* Runs the command in the Jump Host.
    """
        cluster_lock = "icelake"
        run.run_toolbox("jump_ci", "ensure_lock", cluster=cluster_lock)

        print(f"### Running {command}")

    return do_jump_ci


class JumpCi:
    """
    Commands for launching the Jump CI
    """

    def __init__(self):
        self.pre_cleanup_ci = jump_ci("pre_cleanup_ci")
        self.post_cleanup_ci = jump_ci("post_cleanup_ci")
        self.prepare_ci = jump_ci("prepare_ci")
        self.test_ci = jump_ci("test_ci")

        self.generate_plots_from_pr_args = jump_ci("generate_plots_from_pr_args")


def main():
    # Print help rather than opening a pager
    fire.core.Display = lambda lines, out: print(*lines, file=out)

    fire.Fire(JumpCi())


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as e:
        logging.error(f"Command '{e.cmd}' failed --> {e.returncode}")
        sys.exit(1)
