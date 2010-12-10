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
The base class for all command line tools.
"""


import new


class Tool(object):
    """
    Abstract base class for command line tools.
    """
    
    def __init__(self, version=None, description=""):
        """
        Constructor.
        
        :param version: The version description for the tool.
        :type version: string
        """
        
        self.version = version or self.__class__.__name__ + " 0.1"
        self.description = description
        
        self.descriptors = {}
        self._extract()
        
    def _extract(self):
        """
        Extracts all tool methods from the class.
        """
        
        self.descriptors = {}
        for name in dir(self):
            method = getattr(self, name)
            if callable(method) and hasattr(method, 'descriptors'):
                for descriptor in method.descriptors:
                    self.descriptors[descriptor.command] = descriptor
               
    @staticmethod 
    def command_method(command, description, usage):
        """
        Decorator for methods that are used for command line execution.
        """
        
        def describe(function):
            """
            Attach a command descriptor to the decorated method.
            
            :param function: The decorated function.
            :type function: function
            """
            
            indict = {
                'command' : command, 
                'description' : description, 
                'usage' : usage,
                'method' : function.func_name
            }
            descriptor = new.classobj('CommandDescriptor', (), indict)
            
            if not hasattr(function, 'descriptors'):
                function.descriptors = []
            function.descriptors.append(descriptor)
            return function
        return describe
            