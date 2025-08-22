"""
Logging configuration for HyperAI Builder.

Provides structured logging with multiple handlers, formatters,
and integration with external logging services.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger
from loguru._defaults import LOGURU_DEFAULT_LEVELS

from .config import get_settings


class InterceptHandler(logging.Handler):
    """Intercept standard logging and redirect to loguru."""
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, text, simple)
        log_file: Path to log file
    """
    settings = get_settings()
    
    # Use provided values or fall back to settings
    log_level = log_level or settings.log_level
    log_format = log_format or settings.log_format
    
    # Remove default loguru handler
    logger.remove()
    
    # Configure loguru levels
    logger.level("TRACE", no=5, color="<blue>", icon="🔍")
    logger.level("DEBUG", no=10, color="<cyan>", icon="🐛")
    logger.level("INFO", no=20, color="<green>", icon="ℹ️")
    logger.level("SUCCESS", no=25, color="<green>", icon="✅")
    logger.level("WARNING", no=30, color="<yellow>", icon="⚠️")
    logger.level("ERROR", no=40, color="<red>", icon="❌")
    logger.level("CRITICAL", no=50, color="<red>", icon="🚨")
    
    # Console handler
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        if log_format == "json":
            file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
        else:
            file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
        
        logger.add(
            log_file,
            format=file_format,
            level=log_level,
            rotation="10 MB",
            retention="30 days",
            compression="gz",
            backtrace=True,
            diagnose=True,
        )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Intercept specific loggers
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).handlers = []
        logging.getLogger(logger_name).propagate = True
    
    # Set loguru as the default logger
    logger.info("Logging configured successfully")


def get_logger(name: str) -> "logger":
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """
    Log function call with parameters.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    logger.debug(f"Function call: {func_name}", extra={"function": func_name, "params": kwargs})


def log_function_result(func_name: str, result: Any, execution_time: float) -> None:
    """
    Log function execution result and timing.
    
    Args:
        func_name: Name of the function executed
        result: Function result
        execution_time: Execution time in seconds
    """
    logger.info(
        f"Function completed: {func_name}",
        extra={
            "function": func_name,
            "execution_time": execution_time,
            "result_type": type(result).__name__,
        }
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an error with context information.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logger.error(
        f"Error occurred: {str(error)}",
        extra={"error_type": type(error).__name__, "context": context or {}},
        exc_info=True,
    )


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event
        details: Event details
    """
    logger.warning(
        f"Security event: {event_type}",
        extra={"event_type": event_type, "details": details},
    )


def log_performance_metric(metric_name: str, value: float, unit: str = "ms") -> None:
    """
    Log performance metrics.
    
    Args:
        metric_name: Name of the performance metric
        value: Metric value
        unit: Unit of measurement
    """
    logger.info(
        f"Performance metric: {metric_name} = {value}{unit}",
        extra={"metric_name": metric_name, "value": value, "unit": unit},
    )


# Context manager for timing operations
class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = logger.start_timer()
        logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            elapsed = logger.stop_timer(self.start_time)
            logger.info(f"Operation completed: {self.operation_name} in {elapsed:.3f}s")
            if exc_type:
                logger.error(f"Operation failed: {self.operation_name}", exc_info=True)


# Decorator for timing functions
def time_function(func):
    """Decorator to time function execution."""
    def wrapper(*args, **kwargs):
        with TimerContext(func.__name__):
            return func(*args, **kwargs)
    return wrapper