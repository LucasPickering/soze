from ccs.core.color import BLACK


def _get_static_color():
    from ccs.core import user_settings  # Workaround!!
    return user_settings.led_static_color


# Maybe not the prettiest solution but it's definitely terse
_MODE_DICT = {
    'off': lambda: BLACK,
    'static': _get_static_color,
}


def get_color(mode):
    """
    @brief      Gets the current color for the LEDs.

    @param      mode  The current LED mode, as a string

    @return     The current LED color, based on mode and other relevant settings.

    @raises     ValueError if the given LED mode is unknown
    """
    try:
        mode_func = _MODE_DICT[mode]  # Get the function used for this mode
    except KeyError:
        valid_modes = _MODE_DICT.keys()
        raise ValueError(f"Invalid mode '{mode}'. Valid modes are {valid_modes}")
    return mode_func()
