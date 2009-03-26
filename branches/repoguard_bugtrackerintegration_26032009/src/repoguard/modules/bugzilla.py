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
BugzillaConnector

"""


import re

from bugz import Bugz


class Bugzilla(object):
    """
        Class to get/push informations from/to single Bugzilla tickets
    """
    def __init__(self, config):
        """ Constructor
        creates a Bugz instance
        
        :param issue_id: the issue id given by the commit msg
        :type issue_id: int
        :param transtaction: transaction informations
        :type transaction: Transaction
        """

        self.bugz = Bugz(config.url, config.user, config.password)
        self.pattern = re.compile(config.pattern, re.IGNORECASE)
        self.issue = False

    def _get_bug(self, bug_id):
        """ 
        returns the Bug if it exists
    
        :return: XML view of one Bug or nothing
        :rtype: ElemenTree object or None
        """
        
        if not self.issue:
            self.issue = self.bugz.get(bug_id)
        return self.issue
    
    def parse_msg(self, msg):
        """
        Extract all issue ids from the given msg.
        """
        
        return self.pattern.findall(msg)
    
    def issue_exists(self, bug_id):
        """ 
        checks if an issue exists, and returns an info if not
        
        :return: Failure message and exitcode
        :rtype: list
        """

        return True if self._get_bug(bug_id) else False
    
    def get_status(self, bug_id):
        """ 
        returns the status of an issue in Bugzilla
            
        :return: Bug status
        :rtype: String
        """
        if not self.issue:
            self.issue = self._get_bug()
        status = self.issue.find(".//bug_status").text
        return status
        
    def get_handler(self, bug_id):
        """ 
        returns the assigned Developer
            
        because all bugzilla user are associated with an email address
        this methods cuts it to make it possible to compare the usernames  
    
        :return: assigned developer
        :rtype: String
        """
        
        issue = self._get_bug(bug_id)
        assigned = issue.find(".//assigned_to").text
        
        return assigned.split("@")[0]
            
    def add_comment(self, bug_id, comment):
        """ 
        adds a comment for a Issue in Bugzilla
            
        :param comment_to_add: new comment msg
        :type comment_to_add: String
        """ 
        self.bugz.modify(bug_id, comment=comment)