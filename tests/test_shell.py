"""Unit tests for stages 1-2 of the Variant 11 shell emulator."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.main import (
    EXIT_ERROR,
    EXIT_OK,
    Shell,
    ShellError,
    main,
    repl,
    run_script,
    vfs_name,
)


def capture(function, *args):
    """Call ``function`` and return (result, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = function(*args)
    return result, out.getvalue(), err.getvalue()


class ShellTests(unittest.TestCase):
    """Prompt, parser and commands."""

    def setUp(self):
        """Create a shell named ``demo``."""
        self.shell = Shell("demo")

    def fails(self, line):
        """Assert that the line raises ShellError; return the message."""
        with self.assertRaises(ShellError) as context:
            self.shell.execute(line)
        return str(context.exception)

    def test_prompt_contains_vfs_name(self):
        """The prompt contains the VFS name."""
        self.assertEqual(self.shell.prompt(), "demo:/$ ")

    def test_vfs_name_from_path(self):
        """The name is the last component of the VFS path."""
        self.assertEqual(vfs_name("some/dir/my_vfs"), "my_vfs")
        self.assertEqual(vfs_name("some/dir/my_vfs/"), "my_vfs")
        self.assertTrue(vfs_name("."))
        self.assertTrue(vfs_name("/"))

    def test_stubs_print_name_and_arguments(self):
        """ls and cd print their name and arguments."""
        self.assertEqual(self.shell.execute("ls"), "ls: args=[]")
        self.assertEqual(self.shell.execute("ls -l /a b"),
                         "ls: args=['-l', '/a', 'b']")
        self.assertEqual(self.shell.execute("cd /var"),
                         "cd: args=['/var']")

    def test_parser_splits_by_whitespace(self):
        """Any amount of spaces and tabs separates the arguments."""
        self.assertEqual(self.shell.execute("  ls \t a    b "),
                         "ls: args=['a', 'b']")

    def test_quotes_keep_spaces(self):
        """A quoted argument stays a single argument."""
        self.assertEqual(self.shell.execute('cd "my dir"'),
                         "cd: args=['my dir']")

    def test_empty_line_and_comments(self):
        """Empty lines and comments do nothing."""
        self.assertEqual(self.shell.execute("   "), "")
        self.assertEqual(self.shell.execute("# comment"), "")
        self.assertEqual(self.shell.execute("ls a # tail"),
                         "ls: args=['a']")
        self.assertEqual(self.shell.execute('ls "a#b"'),
                         "ls: args=['a#b']")

    def test_errors(self):
        """Unknown commands and broken quoting are reported."""
        self.assertIn("unknown command: rm", self.fails("rm file"))
        self.assertIn("parse error", self.fails('ls "oops'))

    def test_exit(self):
        """exit stops the shell; arguments are an error."""
        self.assertIn("usage", self.fails("exit now"))
        self.assertTrue(self.shell.running)
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)


class ScriptAndMainTests(unittest.TestCase):
    """Startup scripts, REPL and entry point."""

    def setUp(self):
        """Create a temporary directory and a shell."""
        self.temp = tempfile.TemporaryDirectory()
        self.shell = Shell("demo")

    def tearDown(self):
        """Remove the temporary directory."""
        self.temp.cleanup()

    def write_script(self, text):
        """Write a script file and return its path."""
        path = Path(self.temp.name) / "script.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def test_script_echoes_input_and_output(self):
        """Commands appear after the prompt, followed by their output."""
        script = self.write_script("# comment\n\nls a\nexit\nls\n")
        code, out, _ = capture(run_script, self.shell, script)
        self.assertEqual(code, EXIT_OK)
        self.assertEqual(out, "demo:/$ ls a\nls: args=['a']\n"
                              "demo:/$ exit\n")

    def test_script_comment_line_not_echoed(self):
        """Comment lines are neither echoed nor executed."""
        script = self.write_script("# hidden\nexit\n")
        _, out, err = capture(run_script, self.shell, script)
        self.assertNotIn("hidden", out)
        self.assertEqual(err, "")

    def test_inline_comment_is_echoed_but_ignored(self):
        """A trailing comment is shown in the echo, not in the args."""
        script = self.write_script("ls a  # note\nexit\n")
        _, out, _ = capture(run_script, self.shell, script)
        self.assertIn("demo:/$ ls a  # note\nls: args=['a']\n", out)

    def test_script_continues_after_error(self):
        """Errors go to stderr and the script goes on."""
        script = self.write_script("rm x\nls\nexit\n")
        _, out, err = capture(run_script, self.shell, script)
        self.assertIn("unknown command: rm", err)
        self.assertIn("ls: args=[]", out)

    def test_missing_script(self):
        """A missing script gives an error and a failure code."""
        code, _, err = capture(run_script, self.shell, Path("nope.txt"))
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("script error", err)

    def test_repl_session(self):
        """Ctrl+C drops the line; exit and Ctrl+D leave the shell."""
        answers = [KeyboardInterrupt(), "ls x", "exit"]
        with mock.patch("builtins.input", side_effect=answers):
            code, out, _ = capture(repl, self.shell)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("ls: args=['x']", out)
        shell = Shell("demo")
        with mock.patch("builtins.input", side_effect=[EOFError()]):
            code, _, _ = capture(repl, shell)
        self.assertEqual(code, EXIT_OK)

    def test_main_prints_debug_and_runs_script(self):
        """main prints every parameter, then runs the script."""
        script = self.write_script("exit\n")
        argv = ["--vfs", "some/my_vfs", "--script", str(script)]
        code, out, _ = capture(main, argv)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("--vfs    = some/my_vfs", out)
        self.assertIn(f"--script = {script}", out)
        self.assertIn("my_vfs:/$ exit", out)

    def test_main_interactive_marker(self):
        """Without --script the debug output says it is interactive."""
        with mock.patch("builtins.input", side_effect=["exit"]):
            code, out, _ = capture(main, ["--vfs", "v"])
        self.assertEqual(code, EXIT_OK)
        self.assertIn("<interactive>", out)

    def test_main_missing_script(self):
        """A missing script ends with a failure code."""
        argv = ["--vfs", "v", "--script", "no_such.txt"]
        code, _, err = capture(main, argv)
        self.assertEqual(code, EXIT_ERROR)
        self.assertIn("script error", err)


if __name__ == "__main__":
    unittest.main()
