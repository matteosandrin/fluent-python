import httpx
from pathlib import Path

DEST_DIR = Path('downloaded')
BASE_URL = 'https://www.fluentpython.com/data/flags'


def save_flag(img: bytes, filename: str) -> None:
    (DEST_DIR / filename).write_bytes(img)


def get_flag(cc: str) -> bytes:
    url = f'{BASE_URL}/{cc}/{cc}.gif'.lower()
    resp = httpx.get(url, timeout=6.1,
                     follow_redirects=True)
    resp.raise_for_status
    return resp.content
