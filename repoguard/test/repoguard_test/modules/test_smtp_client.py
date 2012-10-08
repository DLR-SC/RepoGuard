# -*- coding: utf-8 -*-
# See the file "LICENSE" for the full license governing this code.


"""
Tests the mail handler.
"""


import smtplib

import mock
import pytest

from repoguard.modules import smtp_client


_MAIL = (
    "From: me@here.com\n"
    "To: to@there.com\n"
    "Subject: subject\n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "Content-Transfer-Encoding: 8bit\n\n"
    "unicöde messäge")
    

class TestMail(object):
    
    def setup_method(self, _):
        self._smtp_client = mock.Mock()
        smtp_client.smtplib.SMTP = mock.Mock(return_value=self._smtp_client)
       
    def test_with_login(self):
        smtp_client_helper = smtp_client.SmtpClientHelper("servername", "25", ("username", "password"), 0)
        smtp_client_helper.send_mail("me@here.com", ["to@there.com"], "subject", unicode("unicöde messäge", "utf-8"))
        
        assert self._smtp_client.login.called
        assert self._smtp_client.sendmail.call_args[0][2] == _MAIL
        assert self._smtp_client.quit.called
        
    def test_without_login(self):
        for smtp_client_helper in [
            smtp_client.SmtpClientHelper(), smtp_client.SmtpClientHelper(credentials=(None, None))]:
        
            smtp_client_helper.send_mail("me@here.com", ["to@there.com"], "subject", "message with test")
            
            assert not self._smtp_client.login.called
            assert self._smtp_client.sendmail.called
            assert self._smtp_client.quit.called

    def test_error_handling(self): 
        # pytest.raises exists: pylint: disable=E1101
        smtp_client_helper = smtp_client.SmtpClientHelper("servername", "80")
        self._smtp_client.sendmail.side_effect = smtplib.SMTPException()
        
        pytest.raises(
            smtplib.SMTPException, smtp_client_helper.send_mail, "me@here.com", ["to@there.com"], "subject", "message")
