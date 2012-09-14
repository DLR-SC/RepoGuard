# See the file "LICENSE" for the full license governing this code.


""" Provides common mail client helper functionality. """


import smtplib


class SmtpClientHelper(object):
    """ Helper class for sending mails via SMTP.
    It supports anonymous and simple user name/password authentication. """
    
    _ENCODING = "UTF-8"
        
    def __init__(self, server_name="localhost", port=0, credentials=None, debug_level=0):
        self._server_name = server_name
        self._port = port
        self._credentials = credentials
        self._debug_level = debug_level
    
    def send_mail(self, sender, receivers, subject, message):
        """
        Sends the mail.
        
        :raise: smtplib.SMTPException. 
        """
        
        smtp_client = self._initialize_mail_client()
        try:
            for receiver in receivers:
                mail = self._create_mail(sender, receiver, subject, message)
                smtp_client.sendmail(sender, receiver, mail)
        finally:
            smtp_client.quit()
        
    def _initialize_mail_client(self):
        smtp_client = smtplib.SMTP(self._server_name, self._port)
        smtp_client.set_debuglevel(self._debug_level)
        if self._credentials:
            user, password = self._credentials
            if user and password:
                smtp_client.login(user, password)
        return smtp_client
    
    def _create_mail(self, from_address, to_address, subject, content):
        message = u"From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"
        message = message % (from_address, to_address, subject, content)
        return message.encode(self._ENCODING)
