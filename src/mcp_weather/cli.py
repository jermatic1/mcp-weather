"""`mcp-weather` command line."""

import argparse
import logging

from mcp_weather import config, serve


def main() -> None:
    parser = argparse.ArgumentParser(prog="mcp-weather")
    commands = parser.add_subparsers(dest="command", required=True)
    sv = commands.add_parser("serve", help="MCP server (streamable HTTP at /mcp)")
    sv.add_argument("--host", default="0.0.0.0")
    sv.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    serve.serve(config.from_env(), args.host, args.port)
