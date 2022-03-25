"""
Utility functions for conversion between slurm time specifications
(see `--time` option for `sbatch`) and Python `datetime.timedelta`
objects.
"""

from datetime import timedelta
import re

__all__ = ["zero", "slurm2delta", "delta2slurm", "round_seconds"]

# slurm has two basic time formats
# 1. days-hours(:minutes(:seconds)?)?, which always has days and hours
# 2. (hours:)?(minutes(:seconds)?), which always has minutes

_daysRE = re.compile(r"(?P<days>\d+)-(?P<hours>2[0-3]|[01]?[0-9])"
                     r"(:(?P<minutes>[0-5]\d)(:(?P<seconds>[0-5]\d))?)?")
_minsRE = re.compile(r"((?P<hours>2[0-3]|[01]?[0-9]):)*?"
                     r"((?P<minutes>((?<=:)[0-5]|(?<!:)\d*)\d)"
                      r"(:(?P<seconds>[0-5]\d))?)")

# convenience for comparisons
zero = timedelta(seconds=0)

def slurm2delta(time_str):
    """Convert a slurm time string into a timedelta object

    Acceptable time formats include "minutes", "minutes:seconds",
    "hours:minutes:seconds", "days-hours", "days-hours:minutes" and
    "days-hours:minutes:seconds".

    Modified from Peter's answer at https://stackoverflow.com/a/51916936

    :param time_str: A string identifying a duration.  (eg. 2:13)
    :return datetime.timedelta: A datetime.timedelta object
    """
    parts = _daysRE.match(time_str)
    if parts is None:
        parts = _minsRE.match(time_str)

    err_str = ("Could not parse any time information from '{}'. "
               "Examples of valid strings: "
               "'2', '2:03', '1:02:03', '2-8', '2-8:05', '2-8:05:20'")
    assert parts is not None, err_str.format(time_str)

    time_params = {
        name: float(param)
        for name, param in parts.groupdict().items()
        if param
    }

    return timedelta(**time_params)

def delta2slurm(delta):
    """Convert a timedelta object into a slurm time string
    """
    return str(delta).replace(" days, ", "-")

def round_seconds(delta):
    """Round timedelta object to nearest second

    More than 500 000 microseconds gets rounded up

    Adapted from https://iqcode.com/code/python/python-datetime-round-to-nearest-hour
    """
    return delta + timedelta(seconds=delta.microseconds // 500_000,
                             microseconds=-delta.microseconds)
