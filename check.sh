#!/usr/bin/env bash
# The one definition of "done" for this repo. Agents must make this pass.
set -euo pipefail
cd "$(dirname "$0")"

# Firmware: build, plus native unit tests once test/ has them.
if command -v pio >/dev/null; then
  pio run -s
  if [ -d test/native ]; then pio test -e native; fi
else
  echo "check.sh: FAIL — PlatformIO not installed (brew install platformio)" >&2
  exit 1
fi

# Pi logger
py=python3
[ -x .venv/bin/python ] && py=.venv/bin/python
if [ -d logger ]; then
  "$py" -m compileall -q logger
  if [ -d logger/tests ]; then "$py" -m pytest -q logger/tests; fi
fi
echo "check.sh: OK"
