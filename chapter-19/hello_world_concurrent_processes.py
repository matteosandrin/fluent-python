import itertools
import time
from multiprocessing import Process, Event, synchronize


def spin(msg: str, done: synchronize.Event):
    for char in itertools.cycle(r'\|/-'):
        status = f'\r{char} {msg}'
        print(status, end='', flush=True)
        if done.wait(0.1):
            print()
            break
        blanks = ' ' * len(status)
        print(f'\r{blanks}\r', end='')


def slow() -> int:
    time.sleep(3)
    return 42


def supervisor() -> int:
    done = Event()
    spinner_process = Process(target=spin, args=('Thinking ...', done))
    spinner_process.start()
    result = slow()
    done.set()
    spinner_process.join()
    return result


def main() -> None:
    result = supervisor()
    print(f'Answer: {result}')


if __name__ == '__main__':
    main()
