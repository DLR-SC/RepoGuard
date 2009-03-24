# pylint: disable-msg=W0232, E1101

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
Test methods for the Mail class.
"""

import datetime
import py.test
import socket

from configobj import ConfigObj

from repoguard.handlers.mail import Mail
from repoguard.testutil import TestRepository, TestProtocol, TestProtocolEntry


local_config = """
addresses=dummy@localhost,
""".splitlines()

remote_config = """
level=1
addresses=x,
sender=x
smtp.server=x
smtp.user=x
smtp.password=x
""".splitlines()

class TestMail:
    
    @classmethod
    def setup_class(cls):
        cls.test_protocol = TestProtocol()
        cls.local_config = ConfigObj(local_config)
        cls.remote_config = ConfigObj(remote_config)
        cls.repository = TestRepository()
        cls.repodir, cls.transaction = cls.repository.create_default()
        cls.handler = Mail(cls.transaction)

    def test_success_subject(self):
        fromID = self.transaction.user_id
        assert self.handler.success_subject() == "SVN update by %s at %s" % (fromID, datetime.datetime.now().strftime("%H:%M - %d.%m.%Y"))

    def test_error_subject(self):
        from_id = self.transaction.user_id
        entry = TestProtocolEntry.error()
        assert self.handler.error_subject(entry.check, entry.result) == \
            "Checkin %s by '%s' in check '%s'" % (entry.result, from_id, entry.check.capitalize())

    def test_create_mail(self):
        sender = "test@test.de"
        receiver = "test2@test.de"
        subject = "asdf"
        content = "ab\nasf"
        assert self.handler.create_mail(sender, receiver, subject, content) == \
            "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (sender, receiver, subject, content)

    def test_local_summarize(self):
        # only runs if you have a local smtp server
        mail = Mail(self.transaction)
        try:
            mail.summarize(self.local_config, self.test_protocol, True)
        except socket.error:
            py.test.skip("You need a local smtp server to run this test.")
            
    def test_remote_summarize(self):
        # only runs if the remote server is reachable
        mail = Mail(self.transaction)
        try:
            mail.summarize(self.remote_config, self.test_protocol, True)
        except socket.error:
            py.test.skip("Remote smtp server is not reachable.")