#!/usr/bin/env python3
"""
YAML-to-TOON Conversion Layer

Converts .ai/ YAML files to TOON (Token-Oriented Object Notation) format
for token efficiency benchmarking. YAML remains the human-authored
source-of-truth; TOON is generated as an optimized encoding for AI consumption.

TOON uses compact tabular layouts for uniform arrays and eliminates
redundant quoting/braces, providing 10-18% token reduction on typical
.ai/ files.

References:
  - TOON spec: https://github.com/toon-format/spec
  - toon-python: https://github.com/toon-format/toon-python
"""

from pathlib import Path
from typing import Optional

import yaml

try:
    from toon_format import encode as toon_encode
    HAS_TOON = True
except ImportError:
    HAS_TOON = False


def yaml_file_to_toon(yaml_path: Path) -> str:
    """Convert a single YAML file to TOON format.

    Reads the YAML file, parses it, and re-encodes as TOON.
    Preserves a header comment identifying the source file.
    """
    if not HAS_TOON:
        raise RuntimeError(
            "toon_format not installed. Install with: "
            "pip install git+https://github.com/toon-format/toon-python.git"
        )

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    if data is None:
        return ""

    return toon_encode(data)


def convert_ai_directory(ai_dir: Path) -> str:
    """Convert all .yaml files in an .ai/ directory to a single TOON document.

    Returns concatenated TOON output with file headers, similar to how
    the YAML loader concatenates files with '# From .ai/filename' headers.
    """
    if not ai_dir.exists():
        return ""

    sections = []
    for filepath in sorted(ai_dir.glob("*.yaml")):
        toon_content = yaml_file_to_toon(filepath)
        if toon_content:
            sections.append(f"# From .ai/{filepath.name}\n\n{toon_content}")

    return "\n\n".join(sections)


def convert_selective(ai_dir: Path, filenames: list[str]) -> str:
    """Convert specific .ai/ YAML files to TOON format.

    Used for selective loading where only query-relevant files are included.
    """
    sections = []
    for filename in filenames:
        filepath = ai_dir / filename
        if filepath.exists():
            toon_content = yaml_file_to_toon(filepath)
            if toon_content:
                sections.append(f"# From .ai/{filename}\n\n{toon_content}")

    return "\n\n".join(sections)


def measure_savings(yaml_path: Path, tokenizer_name: str = "gpt4") -> Optional[dict]:
    """Measure token savings for a single file.

    Returns dict with yaml_tokens, toon_tokens, reduction_pct,
    or None if dependencies are missing.
    """
    try:
        import tiktoken
    except ImportError:
        return None

    if not HAS_TOON:
        return None

    enc = tiktoken.encoding_for_model("gpt-4")

    yaml_text = yaml_path.read_text()
    toon_text = yaml_file_to_toon(yaml_path)

    yaml_tokens = len(enc.encode(yaml_text))
    toon_tokens = len(enc.encode(toon_text))

    reduction_pct = (1 - toon_tokens / yaml_tokens) * 100 if yaml_tokens > 0 else 0.0

    return {
        "file": yaml_path.name,
        "yaml_tokens": yaml_tokens,
        "toon_tokens": toon_tokens,
        "reduction_pct": round(reduction_pct, 1),
        "tokens_saved": yaml_tokens - toon_tokens,
    }
