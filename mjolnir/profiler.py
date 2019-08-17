__author__ = "Nghia Doan"
__copyright__ = "Copyright 2018"
__version__ = "1.0.0"
__maintainer__ = "Nghia Doan"
__email__ = "nghia71@gmail.com"
__status__ = "stable"

import copy
from functools import wraps
import threading
import time


class ShareState:
    """
    Shared state class
    """
    _shared_state_ = dict()

    def __init__(self):
        self.__dict__ = self._shared_state_


class ProfileData(ShareState):
    """
    Global dictionary to hold profiling information,
    implemented as a singleton, using RLock to allow re-entrant
    locking for multiple thread adding data entries.
    """
    _lock = threading.RLock()

    def __init__(self):
        ShareState.__init__(self)
        self.data = dict()

    def add_entry(self, function_name, elapsed_time):
        with self._lock:
            if function_name not in self.data:
                self.data[function_name] = [0, [], 0]

            self.data[function_name][0] += 1
            self.data[function_name][1].append(elapsed_time)
            self.data[function_name][2] += elapsed_time

    def get_data(self):
        with self._lock:
            data_copy = copy.deepcopy(self.data)
        return data_copy

    def clear_data(self):
        with self._lock:
            self.data.clear()


PROF_DATA = ProfileData()


def profile(fn):
    """ @profile decorator
    - Wraps around a function, recording start and end time before and
    after executing it.
    - Adding function execution time to the global dictionary
    :param fn: function to be profiled
    :return: profiler wrapped function (decorating), return value
    (of function execution)
    """
    @wraps(fn)
    def with_profiler(*args, **kwargs):
        start_time = int(round(time.time() * 1000))
        ret = fn(*args, **kwargs)
        elapsed_time = int(round(time.time() * 1000)) - start_time
        PROF_DATA.add_entry(fn.__name__, elapsed_time)
        return ret

    return with_profiler


def print_profile_statistics():
    """ Print profiling statistics (collected information) to console
     Calculate max and average execution time of each profiled function
     and print out to console
    :return: None
    """
    print("--- Profiling statistics ---")
    data = PROF_DATA.get_data()
    for func_name, data in sorted(data.items()):
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print(
            "\t {0:45s} called: {1:10d}, total: {2:10d}, "
            "max: {3:10d}, average: {4:20f}".format(
                func_name, data[0], data[2], max_time, avg_time
            )
        )


def log_profile_statistics(logger):
    """ Log profiling statistics (collected information) to given logger
     Calculate max and average execution time of each profiled function
     and write to logger
    :return: None
    """
    logger.info("--- Profiling statistics ---")
    data = PROF_DATA.get_data()
    for func_name, data in sorted(data.items()):
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        logger.info(
            "\t {0:55s} called: {1:10d}, total: {2:10d}, "
            "max: {3:10d}, average: {4:20f}".format(
                func_name, data[0], data[2], max_time, avg_time
            )
        )


def clear_prof_data():
    """ Clear collected profiling information, useful when executing
    repeatedly certain functions and need comparison
    :return: None
    """
    PROF_DATA.clear_data()
