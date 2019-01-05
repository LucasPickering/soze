import argparse
import curses

from soze_display.display import SozeDisplay


def main(stdscr):
    parser = argparse.ArgumentParser(
        description="Curses-based LED/LCD mock display"
    )
    parser.add_argument(
        "--redis",
        "-r",
        default="redis://localhost:6379",
        help="URL for the Redis host",
    )
    args = parser.parse_args()

    SozeDisplay(args.redis).run()


curses.wrapper(main)
