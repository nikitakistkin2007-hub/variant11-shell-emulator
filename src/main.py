"""Variant 11 shell emulator, stages 1-2: REPL and configuration."""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_ERROR = 1
FILE_ENCODING = "utf-8"
COMMENT_CHAR = "#"
FALLBACK_VFS_NAME = "vfs"
STEP = 1
NO_ARGS = 0


class ShellError(Exception):
    """Raised for command execution errors."""


def vfs_name(path: str) -> str:
    """Return the VFS name shown in the prompt for a VFS path."""
    return Path(path).resolve().name or FALLBACK_VFS_NAME


class Shell:
    """Command interpreter with stub commands."""

    def __init__(self, name: str):
        """Create a shell whose prompt contains the VFS ``name``."""
        self.name = name
        self.running = True
        self.handlers = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

    def prompt(self) -> str:
        """Return the input prompt containing the VFS name."""
        return f"{self.name}:/$ "

    @staticmethod
    def parse(line: str) -> list[str]:
        """Split a line into command and arguments; drop ``#`` comments."""
        try:
            return shlex.split(line, comments=True)
        except ValueError as exc:
            raise ShellError(f"parse error: {exc}") from exc

    def execute(self, line: str) -> str:
        """Execute one line and return its output."""
        args = self.parse(line)
        if not args:
            return ""
        handler = self.handlers.get(args[0])
        if handler is None:
            raise ShellError(f"unknown command: {args[0]}")
        return handler(args[STEP:])

    @staticmethod
    def _stub(name: str, args: list[str]) -> str:
        """Return the output of a stub: its name and arguments."""
        return f"{name}: args={args}"

    def cmd_ls(self, args: list[str]) -> str:
        """Stub for ``ls``."""
        return self._stub("ls", args)

    def cmd_cd(self, args: list[str]) -> str:
        """Stub for ``cd``."""
        return self._stub("cd", args)

    def cmd_exit(self, args: list[str]) -> str:
        """Stop the emulator."""
        if len(args) > NO_ARGS:
            raise ShellError("usage: exit")
        self.running = False
        return ""


def report_error(exc: object) -> None:
    """Print an error message to stderr, keeping output order."""
    sys.stdout.flush()
    print(f"error: {exc}", file=sys.stderr, flush=True)


def execute_line(shell: Shell, line: str) -> None:
    """Run one input line and print its output or its error."""
    try:
        output = shell.execute(line)
    except ShellError as exc:
        report_error(exc)
        return
    if output:
        print(output)


def run_script(shell: Shell, script: Path) -> int:
    """Run a startup script, echoing every command like a dialog."""
    try:
        lines = script.read_text(encoding=FILE_ENCODING).splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        report_error(f"script error: {exc}")
        return EXIT_ERROR
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith(COMMENT_CHAR):
            continue
        print(f"{shell.prompt()}{line}")
        execute_line(shell, line)
        if not shell.running:
            break
    return EXIT_OK


def repl(shell: Shell) -> int:
    """Interactive loop; Ctrl+C drops the line, Ctrl+D exits."""
    while shell.running:
        try:
            line = input(shell.prompt())
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue
        execute_line(shell, line)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    """Create the command line parser."""
    parser = argparse.ArgumentParser(description="Variant 11 shell emulator")
    parser.add_argument("--vfs", required=True, help="physical VFS path")
    parser.add_argument("--script", help="startup script path")
    return parser


def print_debug(args: argparse.Namespace) -> None:
    """Print every configured parameter (stage 2 debug output)."""
    print("[debug] parameters:")
    print(f"[debug]   --vfs    = {args.vfs}")
    print(f"[debug]   --script = {args.script or '<interactive>'}")


def main(argv: list[str] | None = None) -> int:
    """Program entry point."""
    args = build_parser().parse_args(argv)
    print_debug(args)
    shell = Shell(vfs_name(args.vfs))
    if args.script:
        return run_script(shell, Path(args.script))
    return repl(shell)


if __name__ == "__main__":
    raise SystemExit(main())
