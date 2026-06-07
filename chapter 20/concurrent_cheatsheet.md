| | ThreadPoolExecutor | ProcessPoolExecutor | asyncio (async/await) |
|---|---|---|---|
| Best for | I/O-bound blocking code | CPU-bound work | I/O-bound async-native code |
| Parallelism | Concurrent, not true parallel (GIL) | True parallel (separate processes) | Concurrent, single-threaded |
| Overhead | Moderate (thread creation/switching) | High (process spawn, IPC, pickling) | Very low |
| Max practical scale | ~hundreds | ~number of CPU cores | thousands+ |
| Shared memory | Yes (same process) | No (separate memory, needs IPC) | Yes (same thread) |
| GIL impact | Released during blocking C calls | Bypassed entirely | N/A (single thread, no GIL contention) |
| Code requirements | Works with normal blocking functions | Functions/args must be picklable | Requires `async`/`await` and async-compatible libraries |
| Race conditions | Possible (preemptive switching) | Not an issue (separate memory) | Rare (cooperative switching only at `await`) |
