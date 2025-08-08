# Caddy Visitor Count
import asyncio
import os
import json
from functools import partial
from pathlib import Path
from connection_counter import ConnectionCounter


async def main() -> None:
    port = int(os.getenv("SERVER_PORT", "9000"))
    file_path = Path(os.getenv("CONNECTION_FILE_PATH", "connectiondata.json"))
    session_length = float(os.getenv("MAX_SESSION_LENGTH", "1800"))

    counter = ConnectionCounter(file_path, session_length)

    # Start socket server on given port
    # Using a unix socket because this is just for inter-process communication
    # So real network support isn't needed
    callback = partial(handle_socket, counter=counter)
    server = await asyncio.start_server(callback, "0.0.0.0", port)

    print(f"Now listening for incoming connections on {port}")

    # Run server until closed
    # Exiting out of async with server requires server to be closed
    # And server.serve_forever will does what it says on the label
    try:
        async with server:
            await server.serve_forever()
    finally:
        # SIGINT issued, or some other reason to exit, cleanup
        await counter.write_files()


async def handle_socket(
    reader: asyncio.StreamReader, _: asyncio.StreamWriter, counter: ConnectionCounter
) -> None:
    print("Connection Started!")
    while True:
        # Read and process each line as it comes in
        next_line = await reader.readline()
        # If socket is closed then once all data has been consumed an empty bytes object will be returned
        if len(next_line) == 0:
            print("Connection Terminated!")
            break
        # Parse JSON data
        # Note: Try to limit amount of arbitrary data in request
        # By limiting max request size in server
        log_data = json.loads(next_line)
        if log_data["msg"] == "handled request":
            # Log of value being handled
            incoming_ip: str = log_data["request"]["client_ip"]
            counter.see_address(incoming_ip)


if __name__ == "__main__":
    asyncio.run(main())
