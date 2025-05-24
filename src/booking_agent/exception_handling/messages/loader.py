from pathlib import Path

_MESSAGE_DIR = Path(__file__).parent
_CACHE = {}


def load_error_message(error_name: str) -> str:
    if error_name not in _CACHE:
        path = _MESSAGE_DIR / f"{error_name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Missing error message for: {error_name}")
        _CACHE[error_name] = path.read_text(encoding="utf-8")
    return _CACHE[error_name]
