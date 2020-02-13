# -*- coding: utf-8 -*-

import sys


PY3 = sys.version_info[0] == 3


if PY3:
    string_type = str
else:
    string_type = basestring  # noqa: F821


try:  # pragma: no cover
    # FIXME: This import must be kept to avoid a breaking change in environments
    # that install `simplejson`, even in newer Python versions.
    import simplejson as json
except ImportError:
    import json  # noqa: F401

try:
    from urllib.parse import (
        urlparse,
        urljoin,
    )
except ImportError:
    from urlparse import (  # noqa: F401
        urlparse,
        urljoin,
    )
