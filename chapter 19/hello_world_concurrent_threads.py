import itertools
import time
from threading import Thread, Event


def spin(msg: str, done: Event):
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
    spinner_thread = Thread(target=spin, args=('Thinking...', done))
    print(f'spinner_thread object: {spinner_thread}')
    spinner_thread.start()
    result = slow()
    done.set()
    spinner_thread.join()
    return result


def main() -> None:
    result = supervisor()
    print(f'Answer: {result}')


if __name__ == '__main__':
    main()
