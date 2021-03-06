import argparse

from soze_reducer.core.reducer import SozeReducer


parser = argparse.ArgumentParser(description="State manager for LED/LCD")
parser.add_argument(
    "--redis",
    "-r",
    default="redis://localhost:6379",
    help="URL for the Redis host",
)
args = parser.parse_args()

SozeReducer(args.redis).run()
