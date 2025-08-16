import logging
import time
from datetime import datetime
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_agent_start(agent_name: str, params: Dict[str, Any] = None):
    """Log the start of an agent execution."""
    timestamp = datetime.now().isoformat()
    logger.info(f"[{timestamp}] Agent '{agent_name}' started with params: {params}")
    return timestamp

def log_agent_end(agent_name: str, start_time: str, output: Any = None):
    """Log the end of an agent execution."""
    end_time = datetime.now().isoformat()
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    duration = (end_dt - start_dt).total_seconds()
    
    output_size = 0
    if output is not None:
        if isinstance(output, str):
            output_size = len(output)
        elif isinstance(output, (list, dict)):
            output_size = len(str(output))
    
    logger.info(f"[{end_time}] Agent '{agent_name}' completed in {duration:.2f}s with output size: {output_size}")
    return end_time, duration, output_size

def log_error(agent_name: str, error: Exception):
    """Log an error that occurred during agent execution."""
    timestamp = datetime.now().isoformat()
    logger.error(f"[{timestamp}] Error in agent '{agent_name}': {str(error)}")