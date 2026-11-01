"""
Export a PsychoPy ``.psyexp`` experiment to a complete, runnable Pavlovia (PsychoJS)
project folder.

This is the Python half of the web-mode Pavlovia workflow. It runs *outside* the
browser (in Google Colab or on a server) where Python and PsychoPy are available:

    web Builder (browser)  ->  .psyexp  ->  [this module]  ->  Pavlovia project folder

The produced folder has the standard Pavlovia layout::

    <out_dir>/
        index.html
        <name>.js                 # the experiment (ES module)
        lib/psychojs-<ver>.js     # the PsychoJS library (downloaded from lib.pavlovia.org)
        lib/psychojs-<ver>.css
        ...

This exporter relies on a PsychoPy build whose ``contrib/javascripton`` transpiler is
active (see ``sync-from-github.sh``). That transpiler converts the Python in code
params to JS (``False`` -> ``false``, ``None`` -> ``null``, ``random()`` ->
``Math.random()``), so no post-processing of the generated JS is needed here. Write
code params in the "blessed" JS-compatible form (e.g. ``1 + random()`` rather than
``random.uniform(1, 2)``) and the raw ``writeScript`` output is already valid.

Usage::

    python export.py <experiment.psyexp> <output_dir>
"""

from __future__ import annotations

import sys
from pathlib import Path


def export_psychojs(psyexp_path, out_dir) -> Path:
    """Export a ``.psyexp`` to a complete Pavlovia project in ``out_dir``.

    Returns the path to the created project directory.
    """
    # imported lazily so the module can be imported where PsychoPy is not installed
    from psychopy import logging as psychopy_logging
    from psychopy.experiment import Experiment
    from psychopy.tools.servertools import getPsychoJS

    psyexp_path: Path = Path(psyexp_path)
    out_dir: Path = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    exp: Any = Experiment.fromFile(str(psyexp_path))
    name: Any | str = exp.settings.params["expName"].val or psyexp_path.stem

    # Passing expPath (a .js path) makes writeInitCodeJS emit index.html alongside the
    # experiment script, and keeps expPath set for the duration of the export.
    target_js: str = str(out_dir / f"{name}.js")

    # Keep output clean for the duration of the export.
    previous_level: Any = psychopy_logging.console.level
    psychopy_logging.console.setLevel(psychopy_logging.CRITICAL)
    try:
        js: Any = exp.writeScript(expPath=target_js, target="PsychoJS", modular=True)
    finally:
        psychopy_logging.console.setLevel(previous_level)

    if not isinstance(js, str):
        raise RuntimeError(f"writeScript did not return a JS string (got {type(js).__name__})")

    (out_dir / f"{name}.js").write_text(data=js, encoding="utf-8")

    # Download the PsychoJS library into <out_dir>/lib/
    getPsychoJS(str(out_dir))

    return out_dir


def main(argv=None) -> int:
    argv: list[str] | Any = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("Usage: python export.py <experiment.psyexp> <output_dir>", file=sys.stderr)
        return 1
    project_dir: Path = export_psychojs(psyexp_path=argv[0], out_dir=argv[1])
    print(f"Exported Pavlovia project to {project_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
