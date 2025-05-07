"""
OpenStax CMS Settings

This module imports the appropriate settings based on the environment.
"""

import os

# Determine the environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

# Import the base settings
from .base import *

# Import environment-specific settings
if ENVIRONMENT == 'prod':
    from .prod import *
elif ENVIRONMENT == 'test':
    from .test import *
elif ENVIRONMENT == 'docker':
    from .docker import *
else:
    # Local development
    try:
        from .local import *
    except ImportError:
        pass
