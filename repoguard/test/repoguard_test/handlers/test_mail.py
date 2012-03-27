#
# Copyright 2008 German Aerospace Center (DLR)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Tests the mail handler.
"""


from configobj import ConfigObj
import mock

from repoguard.handlers import mail


_LOCAL_CONFIG = """
addresses=dummy@localhost,
"""

_REMOTE_CONFIG_WITH_LOGIN = """
level=1
addresses=x,
sender=x
smtp.server=x
smtp.user=x
smtp.password=x
"""

_REMOTE_CONFIG_WITHOUT_LOGIN = """
level=1
addresses=x,
sender=x
smtp.server=x
"""

_SUCCESS_MAIL = """From: me@localhost\r
To: dummy@localhost\r
Subject: SVN update by me at 16:46 - 22.03.2012\r
\r
Protocol

--------------------------------------------------

Check: Result
"""

_ERROR_MAIL = """From: me@localhost\r
To: dummy@localhost\r
Subject: Checkin Result by 'me' in check 'Check'\r
\r
Protocol

--------------------------------------------------

Check: Result
"""


class TestMail(object):
    
    @classmethod
    def setup_class(cls):
        cls._mock_datetime_and_gethostname()
        cls._default_config = ConfigObj(_LOCAL_CONFIG.splitlines())
        cls._handler = mail.Mail(mock.Mock(user_id="me"))
        
    @staticmethod
    def _mock_datetime_and_gethostname():
        mail.socket.gethostname = mock.Mock(return_value="localhost")
        mail.datetime.datetime = mock.Mock()
        strftime_mock = mock.Mock()
        strftime_mock.strftime.return_value = "16:46 - 22.03.2012"
        mail.datetime.datetime.now.return_value = strftime_mock
        
    def setup_method(self, _):
        self._smtp_client = mock.Mock()
        mail.smtplib.SMTP = mock.Mock(return_value=self._smtp_client)
        
    def test_success_mail(self):
        protocol = self._get_protocol(success=True) 
        self._handler.summarize(self._default_config, protocol, True)
        assert self._smtp_client.sendmail.call_args[0][2] == _SUCCESS_MAIL
        
    def test_error_mail(self):
        protocol = self._get_protocol(success=False) 
        self._handler.summarize(self._default_config, protocol, True)
        assert self._smtp_client.sendmail.call_args[0][2] == _ERROR_MAIL
        
    def test_remote_smtp_with_login(self):
        protocol = self._get_protocol(success=True)
        config = ConfigObj(_REMOTE_CONFIG_WITH_LOGIN.splitlines())
        self._handler.summarize(config, protocol, True)
        assert self._smtp_client.quit.called
        
    def test_remote_smtp_without_login(self):
        protocol = self._get_protocol(success=True)
        config = ConfigObj(_REMOTE_CONFIG_WITH_LOGIN.splitlines())
        self._handler.summarize(config, protocol, True)
        self._smtp_client.login.assert_called_once_with("x", "x")
        
    @staticmethod
    def _get_protocol(success=True):
        protocol = mock.MagicMock()
        protocol.__str__.return_value = "Protocol"
        protocol.filter.return_value = protocol
        entry = mock.MagicMock(success=success, check="Check", result="Result")
        entry.__str__.return_value = "Check: Result"
        protocol.__iter__ = lambda _: iter([entry])
        return protocol
