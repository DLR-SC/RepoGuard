#!/usr/bin/env python
# encoding: utf-8
# pylint: disable-msg=W0231
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
# See the License for the speccd mific language governing permissions and
# limitations under the License.
"""
Module to interact with Trac

:Classes:
    Trac

"""

import re
import xmlrpclib


class Trac(object):
    """
    Class to get/push informations from/to single Trac tickets
    """
    
    def __init__(self, config):
        """
        Constructor
        """
        login_url = get_login_url(config.url, config.user, config.password)
        self.server = xmlrpclib.ServerProxy(login_url)
        self.ticket = []
        self.pattern = re.compile(config.pattern, re.IGNORECASE)

    def issue_exists(self, bug_id):
        """
        Checks if an issue-id exists in the bug tracking system
         
        :param issue_id: optional Parameter (for testing purposes)
        :return: boolean value
        """
        
        self._get_ticket(bug_id)
        
        if self.ticket:
            return True
        
        return False
        
        
    def get_status(self, bug_id):
        """
        returns the status of an issue
        :return: status message as a string
        """
     
        if not self.ticket:
            self._get_ticket(bug_id)
        
        return self.ticket[3]["status"]
    
    def get_handler(self, bug_id):
        """
        returns the assigned developer of an issue
        
        :return: assignee as a string
        """
        
        if not self.ticket:
            self._get_ticket(bug_id)
            
        return self.ticket[3]["owner"]
    
    
    def add_comment(self, bug_id, comment):
        """
        adds a comment to the actual issue
        
        :param comment: the comment to add at issue
        :return: boolean of success or failure
        """
 
        if not self.ticket:
            self._get_ticket(bug_id)
            
        return self.server.ticket.update(bug_id, comment)
    
    def _get_ticket(self, bug_id):
        """
        load the ticket from the trac-Server into a local variable.
        """
        
        if not self.ticket:
            try:
                self.ticket = self.server.ticket.get(bug_id)
            except:
                pass
        
                
def get_login_url(url, user, password):
    """
    get login Url

    :param user: ist der User
    
    :arguments:
      url
        the url to the Trac-installation with /login/xmlprc at the end
                
      user
        username of the user to log in
            
      password
        password of the user to log in
    
    **Usage**
    
    >>> get_login_url("http://localhost/login/xmlrpc", "stefan", "nafets")
    'http://stefan:nafets@localhost/login/xmlrpc'
    """ 
    
    splitted = url.split("//", 1)
    scheme, uri = 'http', splitted[0] if len(splitted) == 1 else splitted
    return "%s//%s:%s@%s" % (scheme, user, password, uri)

