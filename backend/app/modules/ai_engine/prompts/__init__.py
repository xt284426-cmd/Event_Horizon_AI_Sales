from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parent


def load_prompt(name: str) -> str:
    """Load a prompt template from this package without allowing path traversal."""

    if Path(name).name != name:
        raise ValueError("Prompt name must be a filename")
    path = PROMPT_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template not found: {name}")
    return path.read_text(encoding="utf-8")


__all__ = ["load_prompt"]
