import sys
from pathlib import Path

from loguru import logger

CLEAR_LOG_ON_EVERY_RUN = True

if CLEAR_LOG_ON_EVERY_RUN:
    if (x := Path("debug.log")).is_file():
        x.unlink()

logger.remove(0)
logger.level("INFO", color="<white>")
logger.level("WARNING", color="<light-red>")

logger.add(
    sink="debug.log", level="DEBUG", rotation="00:00", retention="1 day", colorize=False
)

logger.add(
    sink=sys.stderr,
    level="INFO",
)