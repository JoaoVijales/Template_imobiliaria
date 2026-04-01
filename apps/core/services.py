import logging

logger = logging.getLogger(__name__)


class ContactService:
    def send_contact(self, data: dict) -> None:
        """Log contact for now; extend to send email via SMTP."""
        logger.info(f"Contact from {data['email']}: {data['subject']}")
