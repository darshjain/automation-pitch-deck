import logging
from typing import Dict, Any
from .base import BaseIntegration

logger = logging.getLogger(__name__)

class GmailIntegration(BaseIntegration):
    def __init__(self, api_key: str = "mock_key"):
        self.api_key = api_key

    def listen(self) -> Dict[str, Any]:
        logger.info("Polling Gmail for new threads with 'Pitch Deck' in subject...")
        return {
            "source": "gmail",
            "sender": "founder@startup.com",
            "subject": "Seed Round Pitch Deck",
            "attachment_path": "temp_downloads/deck.pdf",
            "thread_id": "thread_123",
            "context": {
                "source": "gmail",
                "user_id": "founder@startup.com",
                "received_at": "2024-12-28T12:00:00Z"
            }
        }

    def send_reply(self, thread_id: str, content: str) -> bool:
        try:
            logger.info(f"[Gmail] Draft created for thread {thread_id}")
            logger.info(f"   To: founder@startup.com")
            logger.info(f"   Content Preview: {content[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
