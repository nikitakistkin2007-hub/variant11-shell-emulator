"""End-to-end tests: the emulator is started as a real process."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "src" / "main.py"
VFS_DIR = ROOT / "vfs_demo"
SCRIPT = ROOT / "scripts" / "startup.txt"


def run_cli(*args, stdin=""):
    """Run main.py and return the CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(MAIN), *args],
        input=stdin, capture_output=True, text=True, check=False,
    )


class CliTests(unittest.TestCase):
    """Command line parameters and the bundled startup script."""

    def test_vfs_is_required(self):
        """Without --vfs argparse reports an error (exit code 2)."""
        result = run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertIn("--vfs", result.stderr)

    def test_unknown_parameter(self):
        """Unknown parameters are rejected."""
        result = run_cli("--vfs", str(VFS_DIR), "--bogus")
        self.assertEqual(result.returncode, 2)

    def test_missing_script(self):
        """A missing script file gives exit code 1."""
        result = run_cli("--vfs", str(VFS_DIR), "--script", "absent.txt")
        self.assertEqual(result.returncode, 1)
        self.assertIn("script error", result.stderr)

    def test_interactive_session(self):
        """Input from stdin works; the prompt has the VFS name."""
        result = run_cli("--vfs", str(VFS_DIR), stdin="ls -l\nrm x\nexit\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("vfs_demo:/$ ", result.stdout)
        self.assertIn("ls: args=['-l']", result.stdout)
        self.assertIn("unknown command: rm", result.stderr)

    def test_eof_ends_session(self):
        """Ctrl+D (end of input) leaves the emulator cleanly."""
        result = run_cli("--vfs", str(VFS_DIR), stdin="ls\n")
        self.assertEqual(result.returncode, 0)

    def test_debug_output_lists_all_parameters(self):
        """Both parameters are printed at start."""
        result = run_cli("--vfs", str(VFS_DIR), "--script", str(SCRIPT))
        self.assertIn(f"--vfs    = {VFS_DIR}", result.stdout)
        self.assertIn(f"--script = {SCRIPT}", result.stdout)

    def test_bundled_script(self):
        """The bundled script runs to its exit command."""
        result = run_cli("--vfs", str(VFS_DIR), "--script", str(SCRIPT))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("vfs_demo:/$ ls -l /home docs", result.stdout)
        self.assertIn("ls: args=['name with spaces']", result.stdout)
        self.assertNotIn("never executed", result.stdout)
        self.assertEqual(result.stdout.count("ls: args=[]"), 1)


if __name__ == "__main__":
    unittest.main()
