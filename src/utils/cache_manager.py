import hashlib
from pathlib import Path

CACHE_DIR = Path(__file__).parents[2].joinpath('cache')
CACHE_DIR.mkdir(exist_ok=True)

def _url_to_filename(url: str) -> Path:
    # create a hash of the URL for a unique filename
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{url_hash}.html"

def save_cache(url: str, content: str):
    path = _url_to_filename(url)
    path.write_text(content, encoding="utf-8")

def load_cache(url: str) -> str | None:
    path = _url_to_filename(url)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None
