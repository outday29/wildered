import sys
from pathlib import Path

from loguru import logger

logger.remove(0)
logger.level("INFO", color="<white>")
logger.level("WARNING", color="<light-red>")

logger.add(
    sink=sys.stderr,
    level="INFO",
)