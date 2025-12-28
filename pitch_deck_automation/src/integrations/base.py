from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseIntegration(ABC):
    """
    Abstract Base Class for all External Integrations (Gmail, Slack, Drive).
    Follows the Adapter Pattern to normalize inputs/outputs for the Sago Agent.
    """
    
    @abstractmethod
    def listen(self) -> Any:
        """
        Listens for events (e.g., new emails, messages).
        Should return a standardized event object.
        """
        pass

    @abstractmethod
    def send_reply(self, destination: str, content: str) -> bool:
        """
        Sends the agent's response back to the source.
        """
        pass
