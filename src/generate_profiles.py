"""Generate a JSON snapshot of PsychoPy Builder profiles for Studio web mode."""
import argparse
import json
from pathlib import Path
from typing import Any
from argparse import Namespace

def encode_profile_value(value) -> str:
    if isinstance(value, str):
        return str(value)
    raise TypeError(f"Unsupported profile value: {type(value).__name__}")

def generate_profiles(output_path) -> Path:
    from psychopy import __version__
    from psychopy.experiment import (
        getDeviceProfiles,
        getElementProfiles,
        getLoopProfiles,
    )

    snapshot: dict[str, Any] = {
        "metadata": {"psychopyVersion": __version__, "schemaVersion": 1},
        "components": getElementProfiles(),
        "loops": getLoopProfiles(),
        "devices": getDeviceProfiles(),
    }

    content: str = json.dumps(
        snapshot, indent=2, ensure_ascii=False, allow_nan=False,
        default=encode_profile_value,
    )

    output_path: Path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(data=content + "\n", encoding="utf-8")
    return output_path

def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination JSON file")
    args: Namespace = parser.parse_args()
    output_path: Path = generate_profiles(output_path=args.output)
    print(f"Generated Builder profiles: {output_path}")

if __name__ == "__main__":
    main()
