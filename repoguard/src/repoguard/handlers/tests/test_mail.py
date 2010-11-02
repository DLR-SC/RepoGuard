# pylint: disable=C0103
# C0103: __, ___ are not valid argument names but can be used
#        to avoid "unused arguments" Pylint message. Currently,
#        the arguments are not needed in the SMTP mock.
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


import datetime
import smtplib

from configobj import ConfigObj

from repoguard.handlers.mail import Mail
from repoguard.testutil import TestRepository, TestProtocol, TestProtocolEntry


_LOCAL_CONFIG = """
addresses=dummy@localhost,
""".splitlines()

_REMOTE_CONFIG = """
level=1
addresses=x,
sender=x
smtp.server=x
smtp.user=x
smtp.password=x
""".splitlines()


class _SmtpMock(object):
    """ Mocks class smtplib.SMTP. """
    
    def __init__(self, _, __=None):
        """ Constructor does nothing. """
        
        pass
    
    def set_debuglevel(self, _):
        """ Does nothing. """
        
        pass
    
    def login(self, _, __):
        """ Does nothing. """
        
        pass

    def sendmail(self, _, __, ___):
        """ Does nothing. """
        
        pass
    
    def quit(self):
        """ Does nothing. """
        
        pass
    

class TestMail(object):
    """ Tests the mail handler. """
    
    @classmethod
    def setup_class(cls):
        """ Creates the test setup. """
        
        cls.test_protocol = TestProtocol()
        cls.local_config = ConfigObj(_LOCAL_CONFIG)
        cls.remote_config = ConfigObj(_REMOTE_CONFIG)
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        cls.handler = Mail(cls.transaction)
        smtplib.SMTP = _SmtpMock

    def test_success_subject(self):
        """ Tests the mail subject on successful commit. """
        
        from_id = self.transaction.user_id
        assert self.handler.success_subject() == "SVN update by %s at %s" \
               % (from_id, datetime.datetime.now().strftime("%H:%M - %d.%m.%Y"))

    def test_error_subject(self):
        """ Tests the mail subject on unsuccessful commit. """
        
        from_id = self.transaction.user_id
        entry = TestProtocolEntry.error()
        assert self.handler.error_subject(entry.check, entry.result) \
               == "Checkin %s by '%s' in check '%s'" \
               % (entry.result, from_id, entry.check.capitalize())

    def test_create_mail(self):
        """ Tests the mail content. """
        
        sender = "test@test.de"
        receiver = "test2@test.de"
        subject = "asdf"
        content = "ab\nasf"
        assert self.handler.create_mail(sender, receiver, subject, content) \
               == "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" \
               % (sender, receiver, subject, content)

    def test_local_summarize(self):
        """ Tests simple local configuration. """
        
        mail = Mail(self.transaction)
        mail.summarize(self.local_config, self.test_protocol, True)
            
    def test_remote_summarize(self):
        """ Tests remote configuration. """
        
        mail = Mail(self.transaction)
        mail.summarize(self.remote_config, self.test_protocol, True)
