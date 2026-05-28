from concurrent import futures
from primes import NUMBERS, is_prime
from time import perf_counter
from typing import NamedTuple

class PrimeResult(NamedTuple):
    n: int
    prime: bool
    elapsed: int

def check(n: int) -> PrimeResult:
    start = perf_counter()
    prime = is_prime(n)
    return PrimeResult(n, prime, perf_counter() - start)

def check_many(nums: list[int]) -> list[PrimeResult]:
    with futures.ProcessPoolExecutor() as executor:
        res = executor.map(check, nums)
    return list(res)

def main():
    t0 = perf_counter()
    prime_result = check_many(sorted(NUMBERS))
    delta = perf_counter() - t0
    for n, prime, elapsed in prime_result:
        label = 'P' if prime else ' '
        print(f'{n:16} {label} {elapsed:9.6f}s')
    print()
    print(f'{len(prime_result)} prime checks in {delta:.2f}s')

if __name__ == '__main__':
    main()