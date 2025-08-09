# Mostly just following the steps at https://hub.docker.com/_/python/
# Adapting only as needed
FROM docker.io/python:3.13-slim

WORKDIR /usr/src/app

# Install dependencies using frozen to avoid breakages from updates
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copying just the two files I need
COPY main.py connection_counter.py ./

# Allow proxies to communicate from any address
# As this is meant to run behind a reverse proxy
# Change this if you're not doing this
CMD [ "python", "./main.py" ]
