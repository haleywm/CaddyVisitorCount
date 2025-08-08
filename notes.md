# Notes for implementation:

I can't find any convenient libraries to simplify listening on a socket so I'm doing it myself

Easiest way to do this and safely multitask is to create my own asyncio event loop, with the main loop being a method which uses [start_server](https://docs.python.org/3.10/library/asyncio-stream.html#asyncio.start_server) to listen on a given port for network logs. This start_server call can then spawn StreamReaders for any incoming communications, and those StreamReaders can then interact with some sort of async safe class that I'll develop, which can update internally tracked values as needed, and use [aiofiles](https://pypi.org/project/aiofiles/) to write out an output file somewhere accessible by the file server.

```Python
VisitorTracker:
    tracked_ips: dict[ip_address, last_seen]
    current_visitors
    total_visitors
```

When program starts, read output file if it exists to set value for current_visitors. Current visitors is the current number of visitors in tracked_ips. Tracked ip's stores unique IPs and the time they were last seen. Every {10 minutes, configurable}, IPs that haven't been seen in the last {30 minutes, configurable} will be purged. Incoming logs will mark an IP as freshly seen, which will increment total visitors and current visitors if this IP is new to the list.
