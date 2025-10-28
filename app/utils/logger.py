"""
Logger Configuration - Structured logging for VisionID
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "visionid", log_file: str = None, level=logging.INFO):
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create default logger
logger = setup_logger(
    name="visionid",
    log_file="logs/visionid.log",
    level=logging.INFO
)


def log_request(endpoint: str, user_id: str = None, status: str = "success"):
    """
    Log API request
    
    Args:
        endpoint: API endpoint
        user_id: User ID if applicable
        status: Request status
    """
    logger.info(f"Request: {endpoint} | User: {user_id or 'N/A'} | Status: {status}")


def log_recognition(user_id: str, confidence: float, success: bool):
    """
    Log face recognition attempt
    
    Args:
        user_id: Recognized user ID
        confidence: Recognition confidence
        success: Recognition success status
    """
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Recognition {status} | User: {user_id} | Confidence: {confidence:.3f}")


def log_registration(user_id: str, name: str, success: bool):
    """
    Log user registration
    
    Args:
        user_id: New user ID
        name: User name
        success: Registration success status
    """
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Registration {status} | User ID: {user_id} | Name: {name}")


def log_attendance(user_id: str, name: str, status: str):
    """
    Log attendance marking
    
    Args:
        user_id: User ID
        name: User name
        status: Attendance status
    """
    logger.info(f"Attendance Marked | User: {name} ({user_id}) | Status: {status}")


def log_error(error_type: str, message: str, details: str = None):
    """
    Log error with details
    
    Args:
        error_type: Type of error
        message: Error message
        details: Additional error details
    """
    error_msg = f"ERROR: {error_type} | {message}"
    if details:
        error_msg += f" | Details: {details}"
    logger.error(error_msg)


def log_performance(operation: str, duration: float, items_processed: int = 1):
    """
    Log performance metrics
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        items_processed: Number of items processed
    """
    avg_time = duration / items_processed if items_processed > 0 else duration
    logger.info(
        f"Performance | Operation: {operation} | "
        f"Duration: {duration:.3f}s | Items: {items_processed} | "
        f"Avg: {avg_time:.3f}s/item"
    )
