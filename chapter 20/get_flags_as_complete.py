from concurrent import futures
from flags import save_flag, get_flag, DEST_DIR
from typing import Callable
import time

POP20_CC = ('CN IN US ID BR PK NG BD RU JP '
            'MX PH VN ET EG DE IR TR CD FR').split()


def download_one(cc: str):
    image = get_flag(cc)
    save_flag(image, f'{cc}.gif')
    return cc


def download_many(cc_list: list[str]) -> int:
    fts = []
    with futures.ThreadPoolExecutor() as executor:
        for cc in cc_list:
            fts.append(executor.submit(download_one, cc))
        for future in futures.as_completed(fts):
            flag = future.result()
            print(flag, end=' ', flush=True)


def main(downloader: Callable[[list[str]], int]) -> None:
    DEST_DIR.mkdir(exist_ok=True)
    t0 = time.perf_counter()
    count = downloader(POP20_CC)
    elapsed = time.perf_counter() - t0
    print(f'\n{count} downloads in {elapsed:.2f}s')


if __name__ == '__main__':
    main(download_many)
