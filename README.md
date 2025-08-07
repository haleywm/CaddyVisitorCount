# Caddy Visitor Count

A tool which generates a number of unique visitors, by receiving [caddy logs over a network port](https://caddyserver.com/docs/json/logging/logs/writer/net/).

This tool was inspired by me wanting to add a "Visitor Count" number to my static website, which I host using Caddy's handy `file_server` directive. I couldn't find any good way to track unique visitors purely using Caddy, and I wasn't satisfied by filtering the `http_requests_total` figure out of the built-in metrics, as this value gets rapidly inflated by any assets used on your website.

## Usage:

TODO
