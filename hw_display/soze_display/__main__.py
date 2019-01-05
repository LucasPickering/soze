import argparse

from soze_display.display import SozeDisplay


parser = argparse.ArgumentParser(description="Hardware-based LED/LCD display")
parser.add_argument(
    "--redis",
    "-r",
    default="redis://localhost:6379",
    help="URL for the Redis host",
)
args = parser.parse_args()

SozeDisplay(args.redis).run()
