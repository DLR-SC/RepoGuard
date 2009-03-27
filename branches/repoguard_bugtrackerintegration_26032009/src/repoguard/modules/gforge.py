# encoding: utf-8
# pylint: disable-msg=

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
Module to handle a connection with GForge.

"""

import re

from suds.xsd.sxbasic import Import
from suds.client import Client


class Gforge(object):  
    """
    Class to get/push informations from/to single GForgs Bugs tickets
    """
    
    def __init__(self, config):
        """
        Constructor
        
        :param config: config object 
        :param transaction: transaction object
        :param issue_ids: string with group_id, artifact_type_id, artifact_id
        """
        
        Import.bind('http://schemas.xmlsoap.org/soap/encoding/')
    
        self.client = Client(config.url)
        self.service = self.client.service
        
        self.hash = self.service.login(config.user, config.password)
        self.issue = {}
        self.pattern = re.compile(config.pattern, re.IGNORECASE)
        
    def _get_bug(self, bug_id):
        """
        searches for a bug in the bug tracking system and extracts the 
        information for:
        
        * Status
        * Username
        
        of a single issue
        """    
        
        # get Bug Informations
        bug = self.service.getTrackerItem(self.hash, bug_id)
        
        if bug[2] == 1:
            self.issue["status"] = "Open"
        elif bug[2] == 2:
            self.issue["status"] = "Closed"
        else: 
            self.issue["status"] = "Error" 
            
        # get User by unixname
        userid = self.service.getTrackerItemAssignees(self.hash, bug_id)
        
        user = self.service.getUser(self.hash, int(userid[0][1]))
        self.issue["user_name"] = str(user[1])
        
    def issue_exists(self, bug_id):
        """
        checks if an issue exists and returns boolean
        """

        return True if self.service.getTrackerItem(self.hash, bug_id) else False
            
    def get_status(self, bug_id):
        """
        returns the status 
        """
        if not self.issue:
            self._get_bug(bug_id)
        
        return self.issue["status"]
            
    def get_handler(self):
        """
        returns the username
        """
        if not self.issue:
            self._get_bug()
        
        return self.issue["user_name"]
    
    def add_comment(self, bug_id, comment):
        """
        adds a comment to the bug tracking system
        
        :param message: the message to ba added (string)
        """
        
        self.service.addTrackerItemMessage(self.hash, bug_id, comment)
        
    def set_revision(self, bug_id, revision):
        pass
        
        

        
        