"""Base package with constants."""
from pathlib import Path

import pkg_resources

__version__ = pkg_resources.get_distribution("sklearn-diabetes-example").version

BASE_PATH = (Path(__file__).parent / "..").resolve()
