import logging
import time
from typing import List, Dict, Any
import threading
from queue import Queue, Empty

from .main import AgentOrchestrator
from .integrations.base import BaseIntegration
from .integrations.gmail_connector import GmailIntegration
from .integrations.slack_connector import SlackIntegration

logger = logging.getLogger("SagoCore")

class SagoSystem:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.connectors: List[BaseIntegration] = []
        self.event_queue = Queue()
        self.is_running = False
        
        self._register_connector(GmailIntegration())
        self._register_connector(SlackIntegration())

    def _register_connector(self, connector: BaseIntegration):
        self.connectors.append(connector)
        logger.info(f"Registered Connector: {connector.__class__.__name__}")

    def start(self):
        self.is_running = True
        logger.info("Sago System Started. Listening for inputs...")
        
        for connector in self.connectors:
            thread = threading.Thread(target=self._poll_connector, args=(connector,))
            thread.daemon = True
            thread.start()

        try:
            while self.is_running:
                try:
                    event = self.event_queue.get(timeout=1.0) 
                    self._process_event(event)
                    self.event_queue.task_done()
                except Empty:
                    continue
                except KeyboardInterrupt:
                    self.stop()
        except KeyboardInterrupt:
            self.stop()

    def _poll_connector(self, connector: BaseIntegration):
        while self.is_running:
            try:
                event = connector.listen()
                if event:
                    logger.info(f"Event Received from {event.get('source')}")
                    self.event_queue.put(event)
                time.sleep(5)
            except Exception as e:
                logger.error(f"Connector Error ({connector.__class__.__name__}): {e}")
                time.sleep(10)

    def _process_event(self, event: Dict[str, Any]):
        source = event.get('source')
        pdf_path = event.get('attachment_path')
        
        if not pdf_path:
            logger.warning(f"Event from {source} has no attachment. Ignoring.")
            return

        logger.info(f"Processing Request from {source}...")
        
        try:
            results = self.orchestrator.run(
                pdf_path, 
                user_context={
                    "user_id": event.get('sender'),
                    "source": source
                }
            )
            
            if results['status'] == 'success':
                reply_content = results['report']
                for conn in self.connectors:
                    if isinstance(conn, GmailIntegration) and source == 'gmail':
                        conn.send_reply(event.get('thread_id'), reply_content)
                    elif isinstance(conn, SlackIntegration) and source == 'slack':
                        conn.send_reply(event.get('channel_id'), reply_content)
                        
        except Exception as e:
            logger.error(f"System Error processing event: {e}")

    def stop(self):
        self.is_running = False
        logger.info("Sago System Stopping...")
