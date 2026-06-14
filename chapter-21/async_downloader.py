# we are trying to crawl many images, and then turn each image to grayscale
# we will use asyncio to drive the concurrent image download
# then use ProcessPoolExecutor to do the actual conversion to grayscale

# we will use a semaphore to limit concurrency

import asyncio
import concurrent.futures
import cv2
import httpx
import numpy as np
import os.path
import sys
from typing import NamedTuple
from urllib.parse import urlparse

DOWNLOAD_PATH = "downloaded/"
MAX_CONCURRENT = 10


class DownloadResult(NamedTuple):
    url: str
    status: int
    image: bytes | None

class Context(NamedTuple):
    client: httpx.AsyncClient
    semaphore: asyncio.Semaphore
    loop: asyncio.AbstractEventLoop
    pool: concurrent.futures.ProcessPoolExecutor

def worker(img: bytes, url: str, target: str):
    ext = url[url.rfind("."):]
    grayscale_img = convert_to_grayscale(img, ext)
    if grayscale_img is None:
        print(
            f"ERROR: Image failed to convert to grayscale: {url}", file=sys.stderr)
        return
    save(grayscale_img, url, target)


def convert_to_grayscale(img: bytes, extension: str) -> bytes | None:
    buffer = np.frombuffer(img, dtype=np.uint8)
    grayscale_array = cv2.imdecode(buffer, cv2.IMREAD_GRAYSCALE)
    if grayscale_array is None or grayscale_array.size == 0:
        return None
    success, encoded_buffer = cv2.imencode(f".{extension}", grayscale_array)
    if success:
        return encoded_buffer.tobytes()
    return None


def save(img: bytes, url: str, target: str):
    parsed = urlparse(url)
    filename = parsed.path[1:].replace("/", ".")
    filepath = os.path.join(target, filename)
    with open(filepath, 'wb') as f:
        f.write(img)
        print(f"INFO: Image saved to disk: {filepath}")


async def download(url: str, ctx: Context) -> DownloadResult:
    try:
        async with ctx.semaphore:
            print(f"INFO: downloading {url}")
            res = await ctx.client.get(url, timeout=10.0)
    except httpx.HTTPError:
        return DownloadResult(url, 0, None)
    if res.status_code == 200:
        return DownloadResult(url, 200, res.content)
    return DownloadResult(url, res.status_code, None)


async def process(
    url: str,
    ctx: Context
):
    res = await download(url, ctx)
    if res.status == 200:
        try:
            await ctx.loop.run_in_executor(ctx.pool, worker, res.image, res.url, DOWNLOAD_PATH)
        except Exception as e:
            print(
                f"ERROR: processing failed for {res.url}: {e}", file=sys.stderr)
    else:
        print(f"ERROR: URL failed to download: {res.url}", file=sys.stderr)


async def download_many(urls: list[str]):
    loop = asyncio.get_running_loop()
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    with concurrent.futures.ProcessPoolExecutor() as pool:
        async with httpx.AsyncClient() as client:
            ctx = Context(client, semaphore, loop, pool)
            await asyncio.gather(*(process(u, ctx) for u in urls))


async def main():
    urls = open("image-urls.txt").read().strip().split("\n")
    urls = [u for u in urls if u.endswith(
        ".png") or u.endswith(".jpg") or u.endswith(".jpeg")]
    if not os.path.exists(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)
    await download_many(urls)

if __name__ == "__main__":
    asyncio.run(main())
