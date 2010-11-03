# pylint: disable-msg=R0903,C0103,W0232
# R0903,C0103,W0232: Caused by class type used for configuration.
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


""" Send the message as E-Mail. """


import smtplib
import socket
import datetime

from repoguard.core.module import ConfigSerializer, Handler, HandlerConfig
from repoguard.core.module import Array, String, Integer


class SMTP(ConfigSerializer):
    """ The SMTP server configuration. """
    class types:
        """ Only the server is required; all other 
        parameters are optionally. """
        
        server = String
        port = Integer(optional=True, default=25)
        user = String(optional=True, default=None)
        password = String(optional=True, default=None)

class Config(HandlerConfig):
    """ General configuration. """
    
    class types(HandlerConfig.types):
        """ Only the destination addresses are required. """
        
        level = Integer(optional=True, default=0)
        sender = String(optional=True)
        addresses = Array(String)
        smtp = SMTP(optional=True)
        

class Mail(Handler):
    """ Performs notification via Email. """
    
    __config__ = Config

    def success_subject(self):
        """ Creates the mail subject when everything is fine. """
        
        from_id = self.transaction.user_id
        date = datetime.datetime.now().strftime("%H:%M - %d.%m.%Y")
        return "SVN update by %s at %s" % (from_id, date)
    
    def error_subject(self, check, result):
        """ Creates the mail subject when there is an error. """
        
        user_id = self.transaction.user_id
        msg = "Checkin %s by '%s' in check '%s'"
        return msg % (result, user_id, check.capitalize())
    
    @staticmethod
    def create_mail(from_address, to_address, subject, content):
        """ 
        Creates the content of the mail. 
        """
        
        msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"
        return msg % (from_address, to_address, subject, content)

    def send_mail(self, subject, receivers, msg, config):
        """ 
        Actually send the message. 
        """

        sender = config.sender or self.transaction.user_id + "@" \
                                  + socket.gethostname()
        
        if config.smtp:
            server = smtplib.SMTP(config.smtp.server, config.smtp.port)
            server.set_debuglevel(config.level)
            if not config.smtp.user is None \
               and not config.smtp.password is None:
                server.login(config.smtp.user, config.smtp.password)
        else:
            server = smtplib.SMTP("localhost")
            server.set_debuglevel(config.level)
        
        for receiver in receivers:
            mail = self.create_mail(sender, receiver, subject, msg)
            server.sendmail(sender, receiver, mail)
        server.quit()
        
    def _summarize(self, config, protocol):
        """ Implements the handler flow. """
        
        subject = self.success_subject()
        msg = str(protocol) + "\n"
        for entry in protocol:
            if not entry.success:
                subject = self.error_subject(entry.check, entry.result)
            if entry.msg:
                msg += "\n" + ("-" * 50) + "\n\n" + str(entry) + "\n"
        self.send_mail(subject, config.addresses, msg, config)
