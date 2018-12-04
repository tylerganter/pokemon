#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

import neighboring modules indirectly through this file

Example:
    from context import web_utils

"""

# Standard library imports
import os
import sys

# Third party imports

# Local application imports


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../..')))

from data_acquisition import settings
