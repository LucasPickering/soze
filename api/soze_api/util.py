import flatten_dict
import re


def to_colon_path(path):
    return re.sub(r"[/.]", ":", path)


def get_at_path(obj, path):
    """Gets a nested value from the given dict.

    Args:
        obj (dict): The dict to drill into
        path (string): The path to the value, separated by colons

    Returns:
        object: The value from the dict at the given path
    """

    d = obj

    # Drill down into the object
    if path:
        for key in path.split(":"):
            d = d[key]

    return d  # Return the object that we ended up with


def _key_reducer(k1, k2):
    if k1:
        return f"{k1}:{k2}"
    return k2


def to_redis(obj, key_prefix):

    # If this is a dictionary, flatten it so it has no nested children
    if isinstance(obj, dict):
        flattened = flatten_dict.flatten(obj, reducer=_key_reducer)
        return {_key_reducer(key_prefix, k): v for k, v in flattened.items()}

    return {key_prefix: obj}


def from_redis(d, key_prefix):
    # If there's only 1 key and it matches the prefix, just return its value
    if len(d) == 1:
        try:
            return d[key_prefix]
        except KeyError:
            pass  # The key doesn't match key_prefix, do normal unflattening

    # Figure out how many groups have to be removed from each key
    key_prefix_len = key_prefix.count(":") + 1 if key_prefix else 0

    # Remove the key prefix from each group as you unflatten it
    return flatten_dict.unflatten(
        d, splitter=lambda key: key.split(":")[key_prefix_len:]
    )
