"""Export annotations from O'Reilly Learning API.

The command fetches JSON responses including annotations from the O'Reilly Learning API.
It then parses annotation metadata to reconstruct their placement in the original XML
document. The built-in exporter then parses the reconstructed XML to send generate
annotation export in the desired format to the standard output stream.
"""
from argparse import ArgumentParser
from pathlib import Path

from .drivers import entry_point


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument(
        "json_dump",
        type=Path,
        help="JSON API response dump; will be created if not exist",
    )
    p.add_argument(
        "--cookies",
        type=str,
        default="cookies",
        help="cookies string or file containing it; obtain this from API request",
    )
    p.add_argument(
        "--export",
        type=str,
        default="csv",
        help="export format, `csv', `raw_xml', or plugin module name",
    )
    p.add_argument(
        "--epub-id",
        action="append",
        help="epub ID/ISBN13 without hyphens for filtering output",
    )

    args = p.parse_args()

    entry_point(**vars(args))


if __name__ == "__main__":
    raise SystemExit(main())
