#
#    Copyright (c) 2011 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
#    $Id: extensions.py 2749 2014-11-29 18:15:24Z tkeffer $
#

"""User extensions module

This module is imported from the main executable, so anything put here will be
executed before anything else happens. This makes it a good place to put user
extensions.
"""

import locale
# This will use the locale specified by the environment variable 'LANG'
# Other options are possible. See:
# http://docs.python.org/2/library/locale.html#locale.setlocale
locale.setlocale(locale.LC_ALL, '')
