import os
import sys

from mongoengine import connect, connection
from pymongo.errors import ConnectionFailure, OperationFailure

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from utils.logger_util import logger


def connect_db():
    """Connect to the MongoDB database."""

    try:
        connect(
            db="finoxa_db",
            host=os.getenv("MONGODB_URI"),
            alias="default",
        )

        logger.info(
            f"Connected to MongoDB successfully: {connection.get_connection().server_info()['ok']}"
        )
    except ConnectionFailure as cf:
        logger.error("Failed to connect to MongoDB:", cf)
        sys.exit(1)

    except OperationFailure as of:
        logger.error("Authentication failed:", of)
        sys.exit(1)
