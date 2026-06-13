import threading
import requests
import queue
import time
import random
from typing import NamedTuple
from concurrent import futures
from collections import defaultdict

URL = "http://localhost:8000"
STOP = object()
stats_lock = threading.Lock()
stop_event = threading.Event()

class CrawlRequest(NamedTuple):
    url: str
    payload: dict


def post_url(url, payload):
    resp = requests.post(url, json=payload)
    return resp.status_code


def producer(q: queue.Queue):
    while not stop_event.wait(0.01):
        random_time = time.time() - random.randint(0, 365*24*60*60)
        iso_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(random_time))
        req = CrawlRequest(URL, { "time": iso_time })
        q.put(req)
   


def worker(q: queue.Queue, stats: defaultdict):
    while True:
        req = q.get()
        if req is STOP:
            q.task_done()
            break
        code = post_url(req.url, req.payload)
        with stats_lock:
            stats[code] += 1
        q.task_done()


def reporter(stats: defaultdict):
    while not stop_event.wait(1.0):
        with stats_lock:
            snapshot = dict(stats)
        lines = ["Stats"] + [f"{code}: {snapshot[code]}" for code in sorted(snapshot.keys())]
        # Clear screen + scrollback, move cursor home, then print
        print("\x1b[3J\x1b[2J\x1b[H" + "\n".join(lines), flush=True)

def empty_queue(q: queue.Queue):
    while not q.empty():
        q.get_nowait()
        q.task_done()

def main():
    num_workers = 10
    q = queue.Queue()
    stats = defaultdict(int)
    stats[200] = stats[400] = 0
    producer_thread = threading.Thread(target=producer, daemon=True, args=(q,))
    reporter_thread = threading.Thread(target=reporter, daemon=True, args=(stats,))
    producer_thread.start()
    reporter_thread.start()
    with futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        fs = [executor.submit(worker, q, stats) for _ in range(num_workers)]
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
            stop_event.set()
            producer_thread.join()
            empty_queue(q)
            for _ in range(num_workers):
                q.put(STOP)
            reporter_thread.join()


if __name__ == "__main__":
    main()
