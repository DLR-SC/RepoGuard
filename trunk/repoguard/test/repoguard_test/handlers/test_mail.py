# -*- coding: utf-8 -*-
# See the file "LICENSE" for the full license governing this code.


"""
Tests the mail handler.
"""


import configobj
import mock

from repoguard.core import constants
from repoguard.core import protocol as protocol_
from repoguard.handlers import mail


_LOCAL_CONFIG = """
addresses=dummy@localhost,
"""

_REMOTE_CONFIG_WITH_LOGIN = """
level=1
addresses=you@there.com,
sender=me@here.com
smtp.server=there
smtp.user=me
smtp.password=secret
"""

_SUCCESS_MAIL = unicode("""Profile 'Default' ran 1 checks with 0 errors. Please continue reading for details.

--------------------------------------------------

Pylint check ran 0ms with the success message:
Something might wänt wröng!
""", "utf-8")

_ERROR_MAIL = unicode("""Profile 'Default' ran 1 checks with 1 errors. Please continue reading for details.

--------------------------------------------------

Pylint check ran 0ms with the error message:
Something might wänt wröng!
""", "utf-8")


class TestMail(object):
        
    def setup_method(self, _):
        self._mail_client = mock.Mock()
        self._patcher = mock.patch("repoguard.handlers.mail.smtp_client.SmtpClientHelper")
        self._mail_class = self._patcher.start()
        self._mail_class.return_value = self._mail_client
        
        self._default_config = configobj.ConfigObj(_LOCAL_CONFIG.splitlines())
        self._handler = mail.Mail(mock.Mock(user_id="me"))
        
    def teardown(self):
        self._patcher.stop()
    
    def test_success_mail(self):
        protocol = self._get_protocol(success=True) 
        self._handler.summarize(self._default_config, protocol, True)
        assert self._mail_client.send_mail.call_args[0][3] == _SUCCESS_MAIL

    @staticmethod
    def _get_protocol(success=True):
        if success:
            result = constants.SUCCESS
        else:
            result = constants.ERROR
        protocol = protocol_.Protocol("Default")
        message = unicode("Something might wänt wröng!", "utf-8")
        entry = protocol_.ProtocolEntry("Pylint", None, result, message)
        protocol.append(entry)
        return protocol
        
    def test_error_mail(self):
        protocol = self._get_protocol(success=False) 
        self._handler.summarize(self._default_config, protocol, True)
        assert self._mail_client.send_mail.call_args[0][3] == _ERROR_MAIL
        
    def test_remote_configuration(self):
        remote_config = configobj.ConfigObj(_REMOTE_CONFIG_WITH_LOGIN.splitlines())
        protocol = self._get_protocol(success=False) 
        self._handler.summarize(remote_config, protocol, True)
        
        assert self._mail_class.call_args[0] == ("there", 25, ("me", "secret"), 1, None)
