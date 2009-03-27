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
General bug tracker configuration.
"""


import re

from repoguard.core.module import ConfigSerializer, String


class Config(ConfigSerializer):
    """
    Base configuration class for bug tracker.
    """
    
    pattern = None
    
    class types(ConfigSerializer.types):
        """
        Configuration parameters.
        """
        
        url = String
        user = String
        password = String(optional=True)
        pattern = String(optional=True, default='BUG[:#]|[\s\-_]ID ([0-9,]+)')
        custom_field = String(optional=True)
        
    def parse_commit_msg(self, commit_msg):
        """
        Method to parse all issue out of a commit message.
        
        :param commit_msg: The commit message that contains the issue ids.
        :type commit_msg: string
        
        :return: A list of issue ids.
        :rtype: list of string
        """
        
        return re.findall(self.pattern, commit_msg, re.IGNORECASE)