from argparse import ArgumentParser
from pathlib import Path

from .drivers import entry_point


def main():
    p = ArgumentParser()
    p.add_argument("json_dump", type=Path, help="JSON dump of API responses")
    p.add_argument(
        "--cookies",
        type=str,
        default="cookies",
        help="Cookies string or file containing it",
    )
    p.add_argument("--export", type=str, default="csv")

    args = p.parse_args()

    entry_point(**vars(args))


if __name__ == "__main__":
    raise SystemExit(main())
