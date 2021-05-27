import logging

import requests

from .config import settings


class SlackGateway:
    """An interface to send data to a Slack incoming webhook."""

    timeout = 5

    def send_message(self, message: str) -> None:
        """Send a message."""
        if settings.SLACK_WEBHOOK:
            self._send(message)
        else:
            print(f"Slack message: {message}")

    def _send(self, message):
        """Submit the message data to the webhook."""
        try:
            requests.post(
                settings.SLACK_WEBHOOK, json={"text": message}, timeout=self.timeout
            )
        except requests.exceptions.RequestException:
            logging.ERROR("slack failed to send message")


slack_gateway = SlackGateway()
