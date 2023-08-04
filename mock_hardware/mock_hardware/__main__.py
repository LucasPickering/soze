import curses

from .display import SozeDisplay


def main(stdscr):
    SozeDisplay().run()


if __name__ == "__main__":
    curses.wrapper(main)
