# Concurrent Programming Cheatsheet

| | ThreadPoolExecutor | ProcessPoolExecutor | async/await |
|---|---|---|---|
| Best for | I/O-bound blocking code | CPU-bound work | I/O-bound async-native code |
| Parallelism | Concurrent, not true parallel (GIL) | True parallel (separate processes) | Concurrent, single-threaded |
| Overhead | Moderate (thread creation/switching) | High (process spawn, IPC, pickling) | Very low |
| Max practical scale | ~hundreds | ~number of CPU cores | thousands+ |
| Shared memory | Yes (same process) | No (separate memory, needs IPC) | Yes (same thread) |
| GIL impact | Released during blocking C calls | Bypassed entirely | N/A (single thread, no GIL contention) |
| Code requirements | Works with normal blocking functions | Functions/args must be picklable | Requires `async`/`await` and async-compatible libraries |
| Race conditions | Possible (preemptive switching) | Not an issue (separate memory) | Rare (cooperative switching only at `await`) |
| Failure isolation | Crash can affect whole process | Crash isolated to subprocess | Crash can affect whole process |
| Typical use cases | File I/O, requests to non-async APIs, blocking SDKs | Image/video processing, number crunching, ML inference | Web servers, network clients, many concurrent connections (aiohttp, asyncpg) |
| Switching trigger | OS-driven, preemptive | N/A (separate processes) | Explicit, only at `await` points |
| Startup cost | Low | High | Very low |

## When should you use each?

**Threads** are better for when you want to run synchronous, I/O bound code concurrently. For example, a lot of libraries in Python do not support `async` natively (two examples: Python's disk I/O library and `requests` ).

The key cost is that you can only run O(hundreds) threads at once, because of their slight overhead.

**Processes** are better for when you need to run truly concurrent, CPU-bound computation (for example: ML inference, simulations, matrix computation). This is because with multiple processes there is no GIL contention, so Python bytecode can be executed on multiple cores simultaneously.

The key cost is that spinning up a new process has a high overhead, so ideally you would want the task performed by the process to be much more resource intensive compared to spinning up a process.

**`async/await`** is better when you have many I/O bound operations that support `async/await` natively. It's much lower overhead than either of the other two options, so it works well for applications with O(thousands+) concurrent operations. Some examples are chatbots, Websockets servers, pipelines with many I/O operations.

The key cost is that all the code has to be `async` compatible.

An applications can use a combination of all three to accomplish different goals:
 * An `asyincio/async/await` loop that handles network I/O and concurrency.
 * Some CPU-heavy tasks offloaded to separate processes on `ProcessPoolExecutor`
 * Any synchronous code that does not support `async/await` is run withing a threa, so that it can run asynchronously (for example, with `asyncio.to_thread()`)