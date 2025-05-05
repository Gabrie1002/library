import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from fastapi import HTTPException
import traceback

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)


handler = RotatingFileHandler("app.log", maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


def log_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as e:
            logger.warning(f"HTTPException: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unhandled Exception: {e}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper

