from pathlib import Path
import os
import aiofiles as aos
import json
import time
import asyncio


class ConnectionCounter:
    max_session_length: float
    total_visitors: int
    file_path: Path
    # Stores IP addresses and when they were last seen
    seen_addresses: dict[str, float]
    # If there has been changes since the last time the file was written
    file_change: bool
    file_lock: asyncio.Lock

    def __init__(self, file_path: Path, max_session_length: float):
        self.max_session_length = max_session_length
        self.file_path = file_path
        self.seen_addresses = dict()
        self.file_change = False
        self.file_lock = asyncio.Lock()
        # Check if data already exists to be loaded or if init is needed
        if file_path.exists() and os.path.getsize(file_path) > 0:
            with open(file_path, "rt") as f:
                data = json.load(f)
                self.total_visitors = data["total_visitors"]
            print(f"Read current total visitors from {file_path}")
        else:
            self.total_visitors = 0
            print(f"No data found at {file_path}, re-initialising visitor count")
            # Save default file
            with open(file_path, "wt") as f:
                json.dump(
                    {
                        "total_visitors": 0,
                        "current_visitors": 0,
                    },
                    f,
                )

    def see_address(self, address: str) -> None:
        current_time = time.time()
        if address not in self.seen_addresses:
            # New session!
            self.total_visitors += 1
            self.file_change = True
            # Schedule file write
            asyncio.create_task(self.write_files())

        self.seen_addresses[address] = current_time
        # Schedule a session check when this session may be due to expire
        asyncio.create_task(self._check_sessions_after(self.max_session_length + 1.0))

    async def write_files(self) -> None:
        # Writes files out if needed
        # Only needed to call from outside of method during cleanup
        async with self.file_lock:
            if self.file_change:
                # Copying current values locally then setting file_change to false again
                cur_visitor_total = self.total_visitors
                cur_visitor_current = len(self.seen_addresses)
                self.file_change = False

                # Writing file out asynchronously
                async with aos.open(self.file_path, "wt") as f:
                    await f.write(
                        json.dumps(
                            {
                                "total_visitors": cur_visitor_total,
                                "current_visitors": cur_visitor_current,
                            }
                        )
                    )

    def _check_sessions(self) -> None:
        # Check if any sessions are older than max age and clear them if they are
        max_allowed_age = time.time() - self.max_session_length
        for address in self.seen_addresses:
            if self.seen_addresses[address] < max_allowed_age:
                # Address hasn't been seen in too long, remove it from list and mark file change
                del self.seen_addresses[address]
                self.file_change = True
        # Schedule a file write if changes occurred
        if self.file_change:
            asyncio.create_task(self.write_files())

    async def _check_sessions_after(self, time: float) -> None:
        await asyncio.sleep(time)
        self._check_sessions()
