#!/usr/bin/env bash
# Calls the emulator with every command line parameter (Linux/macOS).
# Expected failures are shown with their exit codes; the script goes on.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
MAIN="$ROOT/src/main.py"

run() {
    echo
    echo "\$ main.py $*"
    "$PYTHON" "$MAIN" "$@"
    echo "[exit code: $?]"
}

echo "=== --help ==="
run --help

echo
echo "=== --vfs only: interactive mode (input from a pipe) ==="
printf 'ls -l\ncd /tmp\nrm x\nexit\n' | "$PYTHON" "$MAIN" --vfs "$ROOT/vfs_demo"
echo "[exit code: $?]"

echo
echo "=== --vfs and --script ==="
run --vfs "$ROOT/vfs_demo" --script "$ROOT/scripts/startup.txt"
run --vfs . --script "$ROOT/scripts/startup.txt"

echo
echo "=== Parameter errors ==="
run
run --script "$ROOT/scripts/startup.txt"
run --vfs "$ROOT/vfs_demo" --script "$ROOT/scripts/missing.txt"
run --vfs "$ROOT/vfs_demo" --unknown
