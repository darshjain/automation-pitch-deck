import os
import logging
from typing import Dict, Any, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime

logger = logging.getLogger(__name__)

class DBClient:
    def __init__(self, uri: Optional[str] = None):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client: Optional[MongoClient] = None
        self.db: Optional[Any] = None
        self.collection: Optional[Any] = None
        
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=2000)
            self.client.admin.command('ping')
            self.db = self.client["sago_db"]
            self.collection = self.db["pitch_deck_analyses"]
            logger.info("Connected to MongoDB.")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"Could not connect to MongoDB at {self.uri}. Persistence will be disabled. Error: {e}")
            self.client = None

    def save_analysis(self, metadata: Dict[str, Any], claims: list, report: str) -> bool:
        if self.collection is None:
            logger.warning("Skipping DB save (No connection).")
            return False

        try:
            document = {
                "metadata": {
                    "user_id": metadata.get("user_id", "anonymous"),
                    "source": metadata.get("source", "cli"),
                    "filename": metadata.get("filename", "unknown"),
                    "timestamp": datetime.utcnow(),
                    "execution_time_ms": metadata.get("execution_time_ms", 0)
                },
                "analysis": {
                    "claims_count": len(claims),
                    "claims": claims,
                    "final_report": report
                }
            }
            result = self.collection.insert_one(document)
            logger.info(f"[DB] Analysis saved. ID: {result.inserted_id} | User: {document['metadata']['user_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to save to DB: {e}")
            return False

    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
