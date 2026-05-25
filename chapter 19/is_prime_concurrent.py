import sys
from time import perf_counter
from typing import NamedTuple
from multiprocessing import Process, SimpleQueue, cpu_count, queues

from primes import NUMBERS, is_prime

class PrimeResult(NamedTuple):
    n: int
    prime: bool
    elapsed: int

JobQueue = queues.SimpleQueue[int]
ResultQueue = queues.SimpleQueue[PrimeResult]

def check(n: int) -> PrimeResult:
    start = perf_counter()
    prime = is_prime(n)
    return PrimeResult(n, prime, perf_counter() - start)

def worker(jobs: JobQueue, results: ResultQueue) -> None:
    # here the value 0 will stop iteration (it's the poison pill value)
    while n := jobs.get():
        results.put(check(n))
    # this lets the main loop know that the worker is done
    results.put(PrimeResult(0, False, 0.0))

def start_jobs(procs: int, jobs: JobQueue, results: ResultQueue) -> None:
    for n in NUMBERS:
        jobs.put(n)
    for _ in range(procs):
        proc = Process(target=worker, args=(jobs, results))
        proc.start()
        # we put one 0 in the job queue for each process, which will signal to stop
        jobs.put(0)

def report(procs: int, results: ResultQueue) -> int:
    checked = 0
    procs_done = 0
    while procs_done < procs:
        n, prime, elapsed = results.get()
        if n == 0:
            procs_done += 1
        else:
            checked += 1
            label = 'P' if prime else ' '
            print(f'{n:16} {label} {elapsed:9.6f}s')
    return checked

def main():
    procs = cpu_count()
    if len(sys.argv) > 1:
        procs = int(sys.argv[1])
    print(f'Checking {len(NUMBERS)} numbers with {procs} processes')
    start = perf_counter()
    jobs: JobQueue = SimpleQueue()
    results: ResultQueue = SimpleQueue()
    start_jobs(procs, jobs, results)
    checked = report(procs, results)
    elapsed = perf_counter() - start
    print(f'{checked} prime checks in {elapsed:.2f}s')

if __name__ == '__main__':
    main()