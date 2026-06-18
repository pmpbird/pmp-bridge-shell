#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("controller", ROOT / "automation/controller/v1/controller.py")
controller = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(controller)
CONTRACT = json.loads((ROOT / "automation/controller/v1/controller-contract.json").read_text())


class RealContainerIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("docker") is None:
            raise RuntimeError("Docker is required; isolation tests must not be silently skipped")

    def test_root_filesystem_is_read_only_and_host_is_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            outside = Path(d).parent / "pmp-container-host-escape"
            outside.unlink(missing_ok=True)
            with self.assertRaises(controller.ControllerError) as ctx:
                controller.run_verification_commands(
                    workspace,
                    [["python3", "-c", "from pathlib import Path; Path('/pmp-root-escape').write_text('x')"]],
                    30,
                    CONTRACT,
                )
            self.assertEqual(ctx.exception.reason, "deterministic_verification_failed")
            self.assertFalse(outside.exists())

    def test_network_is_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            code = "import socket; s=socket.socket(); s.settimeout(1); s.connect(('1.1.1.1',53))"
            with self.assertRaises(controller.ControllerError):
                controller.run_verification_commands(workspace, [["python3", "-c", code]], 30, CONTRACT)

    def test_background_process_dies_with_container(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            marker = workspace / "background.txt"
            controller.run_verification_commands(
                workspace,
                [["sh", "-c", "(sleep 2; echo escaped > /workspace/background.txt) & exit 0"]],
                30,
                CONTRACT,
            )
            time.sleep(3)
            self.assertFalse(marker.exists(), "background child survived the container boundary")

    def test_only_designated_workspace_is_writable(self):
        with tempfile.TemporaryDirectory() as d:
            workspace = Path(d)
            controller.run_verification_commands(
                workspace,
                [["python3", "-c", "from pathlib import Path; Path('inside.txt').write_text('ok')"]],
                30,
                CONTRACT,
            )
            self.assertEqual((workspace / "inside.txt").read_text(), "ok")


if __name__ == "__main__":
    unittest.main(verbosity=2)
