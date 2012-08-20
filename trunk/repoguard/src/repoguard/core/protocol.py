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
Module that contains all classes that are reponsible for check handler 
communication.
"""


import time

from repoguard.core import constants


def _property(result):
    """
    Property factory for result summarizer.
    
    :param result: The result that has to be summarized.
    :type result: string
    """
    
    def _get_all(protocol):    
        """
        Summarize all entries that has the given result.
        """
        
        return sum([1 for entry in protocol if entry.result == result])
    
    return property(_get_all)

class Protocol(list):
    """
    Protocol class stores all C{ProtocolEntries} that can be handled as a list.
    """
    
    format = "Profile '%(profile)s' ran %(total)d checks with " \
           + "%(errors)d errors. Please continue reading for details."
    
    def __init__(self, profile):
        """
        Constructor.
        
        :param _profile: The _profile name that has to be logged.
        :type profile: C{string}
        """
        
        list.__init__(self)
        
        self.profile = profile
    
    def _get_success(self):
        """
        Getter for the overall protocol success.
        
        :return: The overall result status.
        :rtype: true if it was successful else false.
        """
        
        return self.errors + self.exceptions == 0
    
    def _get_result(self):
        """
        Getter for the result.
        
        :return: Returns the overall result.
        :rtype: string
        """
        
        if self.success:
            return constants.SUCCESS
        else:
            return constants.ERROR
        
    def __str__(self):
        """
        Converts the protocol in a string representation.
        
        :return: The formated string.
        :rtype: string
        """
        
        return self.format % {
            'profile' : self.profile,
            'successors' : self.successors, 
            'warnings' : self.warnings,
            'errors' : self.errors,
            'exceptions' : self.exceptions,
            'total' : len(self), 
            'result' : self.result
        }
        
    def filter(self, include, exclude):
        """
        Filter the protocol by the given checks.
        
        :param is_included: The checks that has to be included.
        :type is_included: list of check names.
        
        :param exclude: The checks that has to be excluded.
        :type exclude: list of check names.
        
        :return: Returns a new filtered protocol instance.
        :rtype: New protocol instance.
        """
        
        protocol = Protocol(self.profile)
        for entry in self:
            if entry.is_included(include, exclude):
                protocol.append(entry)
        return protocol
    
    def clear(self):
        """
        Removes all items from the protocol.
        """
        
        del self[:]
        
    successors = _property(constants.SUCCESS)
    warnings = _property(constants.WARNING)
    exceptions = _property(constants.EXCEPTION)
    errors = _property(constants.ERROR)
    result = property(_get_result)
    success = property(_get_success)
        
class ProtocolEntry(object):
    """
    Defines a entry that can be stored in a C{Protocol} object.
    """
    
    pattern = "%H:%M - %d.%m.%Y"
    
    def __init__(self, check, config, result=constants.ERROR, msg=""):
        """
        Constructor.
        
        :param check: The name of the check.
        :type check: string
        
        :param config: The _config that was executed by the check.
        :type config: Section
        
        :param result: The result of the check execution.
        :type result: SUCCESS/WARNING/ERROR or EXCEPTION
                      
        :param msg: The message that was returned by the check.
        :type msg: string
        """
        
        # Time when a check has started.
        self.start_time = 0.0
        # Time when a check has ended.
        self.end_time = 0.0
        # Check name.
        self.check = check
        # Check configuration.
        self.config = config
        # Result of the check..
        self.result = result
        # Check message.
        self.msg = msg
        
        # Standard to string format.
        self.format = "%(check)s check ran %(duration)sms with the " \
                    + "%(result)s message:\n%(msg)s"
                        
    def __str__(self):
        """
        Converts the C{ProtocolEntry} in a string representation.
        
        :return: The formated string.
        :rtype: string
        """
        
        
        start = time.strftime(self.pattern, time.localtime(self.start_time))
        end = time.strftime(self.pattern, time.localtime(self.end_time))
        
        return self.format % {
            'start_time' : start,
            'end_time' : end,
            'duration' : self.duration, 
            'check' : self.check.capitalize(), 
            'result' : self.result,
            'msg' : self.msg
        }
        
    def _get_success(self):
        """
        Returns the overall success status of a protocol subclass.
        
        :return: The success status of a protocol subclass.
                 - True = C{constants.SUCCESS}
                 - False = C{constants.EXCEPTION}, C{constants.ERROR}
        :rtype: C{boolean}
        """
        
        return self.result in (constants.SUCCESS, constants.WARNING)
    
    def _get_duration(self):
        """
        Getter for the duration of a check run.
        
        :return: The duration in milliseconds.
        :rtype: integer
        """
        diff = self.end_time - self.start_time
        return int(diff * 1000)
    
    def is_included(self, include, exclude):
        """
        Checks if the given entry has to be included.
        
        :param included: The included list.
        :type included: list of check names.
        
        :param exclude: The exclude list.
        :type exclude: list of check names.
        
        :return: Returns true if the check in included else false.
        :rtype: boolean
        """
        
        incl = include is None or self.check in include
        excl = exclude is None or not self.check in exclude
        return incl and excl
    
    def start(self):
        """
        Store the start time.
        """
        
        self.start_time = time.time()
        
    def end(self):
        """
        Store the end time.
        """
        
        self.end_time = time.time()
        
    duration = property(_get_duration)
    success = property(_get_success)