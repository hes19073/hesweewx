#
#    Copyright (c) 2019 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
"""WeeWX logging facility"""

from __future__ import absolute_import

import sys
import logging.config
from six.moves import StringIO

import configobj

import weewx
from weeutil.weeutil import to_int, to_bool

# These values are known only at runtime
if sys.platform == "darwin":
    address = '/var/run/syslog'
    facility = 'local1'
elif sys.platform.startswith('linux'):
    address = '/dev/log'
    facility = 'user'
else:
    address = ('localhost', 514)
    facility = 'user'

# The logging defaults. Note that two kinds of placeholders are used:
#
#  {value}: these are plugged in by the function setup().
#  %(value)s: these are plugged in by the Python logging module.
#
LOGGING_STR = u"""[Logging]
    version = 1
    disable_existing_loggers = False
      
    [[loggers]]
        # Root logger
        [[[root]]]
          level = {log_level}
          propagate = 1
          handlers = syslog,
    
    # Definitions of possible logging destinations
    [[handlers]]
    
        # System logger
        [[[syslog]]]
            level = DEBUG
            formatter = standard
            class = logging.handlers.SysLogHandler
            address = {address}
            facility = {facility}
    
        # Log to console
        [[[console]]]
            level = DEBUG
            formatter = verbose
            class = logging.StreamHandler
            # Alternate choice is 'ext://sys.stderr'
            stream = ext://sys.stdout
    
    # How to format log messages
    [[formatters]]
        [[[simple]]]
            format = "%(levelname)s %(message)s"
        [[[standard]]]
            format = "{process_name}[%(process)d] %(levelname)s %(name)s: %(message)s" 
        [[[verbose]]]
            format = "%(asctime)s  {process_name}[%(process)d] %(levelname)s %(name)s: %(message)s"
            # Format to use for dates and times:
            datefmt = %Y-%m-%d %H:%M:%S
"""


def setup(process_name, user_log_dict):
    """Set up the weewx logging facility"""

    # Create a ConfigObj from the default string. No interpolation (it interferes with the
    # interpolation directives embedded in the string).
    log_config = configobj.ConfigObj(StringIO(LOGGING_STR), interpolation=False)

    # Turn off interpolation in the incoming dictionary. First save the old
    # value, then restore later. However, the incoming dictionary may be a simple
    # Python dictionary and not have interpolation. Hence the try block.
    try:
        old_interpolation = user_log_dict.interpolation
        user_log_dict.interpolation = False
    except AttributeError:
        old_interpolation = None

    # Merge in the user additions / changes:
    log_config.merge(user_log_dict)

    # Restore the old interpolation value
    if old_interpolation is not None:
        user_log_dict.interpolation = old_interpolation

    # Adjust the logging level in accordance with whether or not the 'debug' flag is on
    log_level = 'DEBUG' if weewx.debug else 'INFO'

    # Now we need to walk the structure, plugging in the values we know.
    # First, we need a function to do this:
    def _fix(section, key):
        if isinstance(section[key], (list, tuple)):
            # The value is a list or tuple
            section[key] = [item.format(log_level=log_level,
                                        address=address,
                                        facility=facility,
                                        process_name=process_name) for item in section[key]]
        else:
            # The value is a string
            section[key] = section[key].format(log_level=log_level,
                                               address=address,
                                               facility=facility,
                                               process_name=process_name)

    # Using the function, walk the 'Logging' part of the structure
    log_config['Logging'].walk(_fix)

    # Extract just the part used by Python's logging facility
    log_dict = log_config.dict().get('Logging', {})

    # The root logger is denoted by an empty string by the logging facility. Unfortunately,
    # ConfigObj does not accept an empty string as a key. So, instead, we use this hack:
    try:
        log_dict['loggers'][''] = log_dict['loggers']['root']
        del log_dict['loggers']['root']
    except KeyError:
        pass

    # Make sure values are of the right type
    if 'version' in log_dict:
        log_dict['version'] = to_int(log_dict['version'])
    if 'disable_existing_loggers' in log_dict:
        log_dict['disable_existing_loggers'] = to_bool(log_dict['disable_existing_loggers'])
    if 'loggers' in log_dict:
        for logger in log_dict['loggers']:
            if 'propagate' in log_dict['loggers'][logger]:
                log_dict['loggers'][logger]['propagate'] = to_bool(log_dict['loggers'][logger]['propagate'])

    # Finally! The dictionary is ready. Set the defaults.
    logging.config.dictConfig(log_dict)


def log_traceback(log_fn, prefix=''):
    """Log the stack traceback into a logger.

    log_fn: One of the logging.Logger logging functions, such as logging.Logger.warning.

    prefix: A string, which will be put in front of each log entry. Default is no string.
    """
    import traceback
    sfd = StringIO()
    traceback.print_exc(file=sfd)
    sfd.seek(0)
    for line in sfd:
        log_fn("%s%s", prefix, line)
