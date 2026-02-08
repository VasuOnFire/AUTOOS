"""
Structured JSON logging with distributed tracing support

Provides consistent logging across all AUTOOS components.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
import uuid

# Context variables for distributed tracing
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
workflow_id_var: ContextVar[Optional[str]] = ContextVar("workflow_id", default=None)
agent_id_var: ContextVar[Optional[str]] = ContextVar("agent_id", default=None)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
        }

        # Add trace context if available
        trace_id = trace_id_var.get()
        if trace_id:
            log_data["trace_id"] = trace_id

        workflow_id = workflow_id_var.get()
        if workflow_id:
            log_data["workflow_id"] = workflow_id

        agent_id = agent_id_var.get()
        if agent_id:
            log_data["agent_id"] = agent_id

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ContextLogger:
    """Logger with context injection"""

    def __init__(self, name: str):
        """
        Initialize context logger

        Args:
            name: Logger name (usually module name)
        """
        self.logger = logging.getLogger(name)

    def _log(
        self, level: int, message: str, extra_fields: Optional[Dict[str, Any]] = None
    ) -> None:
        """Internal log method with context"""
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            None,
        )

        if extra_fields:
            record.extra_fields = extra_fields

        self.logger.handle(record)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message"""
        self._log(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message"""
        self._log(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message"""
        self._log(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message"""
        self._log(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message"""
        self._log(logging.CRITICAL, message, kwargs)


def setup_logging(
    level: str = "INFO", log_format: str = "json", log_file: Optional[str] = None
) -> None:
    """
    Configure logging for AUTOOS

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('json' or 'text')
        log_file: Optional file path for logs
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)


def set_trace_context(
    trace_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> str:
    """
    Set distributed tracing context

    Args:
        trace_id: Trace ID (generated if None)
        workflow_id: Workflow ID
        agent_id: Agent ID

    Returns:
        Trace ID
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    trace_id_var.set(trace_id)

    if workflow_id:
        workflow_id_var.set(workflow_id)

    if agent_id:
        agent_id_var.set(agent_id)

    return trace_id


def clear_trace_context() -> None:
    """Clear distributed tracing context"""
    trace_id_var.set(None)
    workflow_id_var.set(None)
    agent_id_var.set(None)


def get_logger(name: str) -> ContextLogger:
    """
    Get context-aware logger

    Args:
        name: Logger name (usually __name__)

    Returns:
        Context logger instance
    """
    return ContextLogger(name)
