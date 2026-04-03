"""
Unit tests for apps.core.services.ContactService.
"""
import logging

from apps.core.services import ContactService


class TestContactService:
    """Tests for ContactService.send_contact()."""

    def test_send_contact_logs_email_in_message(self, caplog):
        with caplog.at_level(logging.INFO, logger='apps.core.services'):
            ContactService().send_contact({
                'name': 'João',
                'email': 'joao@test.com',
                'subject': 'Teste de assunto',
                'message': 'Mensagem de teste',
            })
        assert 'joao@test.com' in caplog.text

    def test_send_contact_logs_subject_in_message(self, caplog):
        with caplog.at_level(logging.INFO, logger='apps.core.services'):
            ContactService().send_contact({
                'name': 'Maria',
                'email': 'maria@test.com',
                'subject': 'Assunto especial',
                'message': 'Outra mensagem',
            })
        assert 'Assunto especial' in caplog.text

    def test_send_contact_does_not_raise(self):
        """send_contact should complete without raising any exception."""
        service = ContactService()
        # Should not raise
        service.send_contact({
            'name': 'Test User',
            'email': 'a@b.com',
            'subject': 'x',
            'message': 'z',
        })

    def test_send_contact_logs_at_info_level(self, caplog):
        with caplog.at_level(logging.DEBUG, logger='apps.core.services'):
            ContactService().send_contact({
                'name': 'Carlos',
                'email': 'carlos@example.com',
                'subject': 'Info level test',
                'message': 'Checking log level',
            })
        # Verify at least one INFO record was emitted
        info_records = [r for r in caplog.records if r.levelno == logging.INFO]
        assert len(info_records) >= 1
