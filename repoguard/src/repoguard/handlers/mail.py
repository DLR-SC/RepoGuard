# pylint: disable-msg=R0903,C0103,W0232
# R0903,C0103,W0232: Caused by class type used for configuration.
# See the file "LICENSE" for the full license governing this code.


""" Send the message as E-Mail. """


import datetime
import socket

from repoguard.core.module import ConfigSerializer, Handler, HandlerConfig
from repoguard.core.module import Array, String, Integer
from repoguard.modules import smtp_client


class SMTP(ConfigSerializer):
    """ The SMTP server configuration. """
    class types:
        """ Only the server is required; all other 
        parameters are optionally. """
        
        server = String
        port = Integer(optional=True, default=25)
        user = String(optional=True, default=None)
        password = String(optional=True, default=None)
        local_hostname = String(optional=True, default=None)

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

    _ENCODING = "UTF-8"
    
    def __init__(self, transaction):
        Handler.__init__(self, transaction)
        
        self._sender = transaction.user_id + "@" + socket.gethostname()

    def _summarize(self, config, protocol):
        mail_client = self._initialize_mail_client(config)
        sender = config.sender or self._sender
        subject, message = self._get_mail_content(protocol)
        mail_client.send_mail(sender, config.addresses, subject, message)
    
    @staticmethod
    def _initialize_mail_client(config):
        if config.smtp:
            mail_client = smtp_client.SmtpClientHelper(
                config.smtp.server, config.smtp.port, 
                (config.smtp.user, config.smtp.password), config.level, config.smtp.local_hostname)
        else:
            mail_client = smtp_client.SmtpClientHelper()
        return mail_client
    
    def _get_mail_content(self, protocol):
        subject = self._get_success_subject()
        message = unicode(protocol) + "\n"
        for entry in protocol:
            if not entry.success:
                subject = self._get_error_subject(entry.check, entry.result)
            if entry.msg:
                message += "\n" + ("-" * 50) + "\n\n" + unicode(entry) + "\n"
        return subject, message
    
    def _get_success_subject(self):
        from_id = self.transaction.user_id
        date = datetime.datetime.now().strftime("%H:%M - %d.%m.%Y")
        return u"SVN update by %s at %s" % (from_id, date)
    
    def _get_error_subject(self, check, result):
        user_id = self.transaction.user_id
        msg = u"Checkin %s by '%s' in check '%s'"
        return msg % (result, user_id, check.capitalize())
