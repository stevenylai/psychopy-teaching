#!/usr/bin/env bash
#
# Export a .psyexp experiment to a runnable Pavlovia (PsychoJS) project.
#
# Usage: ./export.sh <experiment.psyexp>
#
# Uses the local PsychoPy checkout in ./psychopy (fetched by sync-from-github.sh,
# or a git submodule in a teaching repo). That build bundles the
# contrib/javascripton transpiler, so the generated JS needs no post-processing.
#
# Creates .venv (Python 3.12, via uv) if it doesn't exist, updates its
# dependencies either way, then runs src/export.py, writing the Pavlovia
# project to ./target.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PSYEXP="${1:?Usage: ./export.sh <experiment.psyexp>}"
TARGET="${SCRIPT_DIR}/target"
PSYCHOPY_DIR="${SCRIPT_DIR}/psychopy"

# the local PsychoPy checkout must be present (run sync-from-github.sh, or
# `git submodule update --init psychopy` in a teaching repo)
if [ ! -f "$PSYCHOPY_DIR/psychopy/__init__.py" ]; then
    echo "Missing local PsychoPy at $PSYCHOPY_DIR" >&2
    echo "Run ./sync-from-github.sh first (or 'git submodule update --init psychopy')." >&2
    exit 1
fi

# create the venv if it doesn't exist (default to Python 3.12)
PYTHON_VERSION="${AGENT_HUB_PYTHON_VERSION:-3.12}"
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating .venv with Python ${PYTHON_VERSION} ..."
    uv venv "$SCRIPT_DIR/.venv" --python "${PYTHON_VERSION}"
fi

# install/update dependencies (idempotent)
#
# The export only uses psychopy's Builder/codegen (psychopy.experiment) and
# getPsychoJS (a download) – not the runtime (visual/sound/video). So we install
# psychopy WITHOUT its heavy runtime deps (no ffpyplayer, pyglet, sounddevice,
# pyqt6, ...) and add just the packages the export path actually imports. This is
# fast, small, and avoids the ffpyplayer wheel issues entirely. It also works in
# Google Colab, which has no dnf.
#
# psychopy itself is installed from the local ./psychopy checkout (the dev build
# with the working transpiler), not from PyPI.
MINIMAL_DEPS=("esprima" "packaging" "requests" "astunparse" "pyyaml" "pandas" "json_tricks")

install_deps() {
    uv pip install --python "$SCRIPT_DIR/.venv/bin/python" "$@" --no-deps "$PSYCHOPY_DIR" \
        && uv pip install --python "$SCRIPT_DIR/.venv/bin/python" "$@" "${MINIMAL_DEPS[@]}"
}

if ! install_deps; then
    echo "Default package index failed; retrying against pypi.org..." >&2
    install_deps --default-index https://pypi.org/simple
fi

# export
"$SCRIPT_DIR/.venv/bin/python" "$SCRIPT_DIR/src/export.py" "$PSYEXP" "$TARGET"
