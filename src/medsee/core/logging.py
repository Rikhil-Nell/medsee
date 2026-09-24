"""Rich-backed terminal logging configuration."""

import logging

from rich.logging import RichHandler

_configured = False


def setup_logging(level: str = "INFO") -> None:
    """Configure stdlib logging with Rich terminal output."""
    global _configured
    if _configured:
        return

    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
        force=True,
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger."""
    return logging.getLogger(name)
