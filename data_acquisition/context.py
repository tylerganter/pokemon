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
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_path)

from utils import web_utils
from webapp.scripts import settings
