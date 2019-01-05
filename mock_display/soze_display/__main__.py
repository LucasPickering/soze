import curses

from soze_display import display

curses.wrapper(display.main)
