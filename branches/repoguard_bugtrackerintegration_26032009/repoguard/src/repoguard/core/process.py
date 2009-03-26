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
# See the License for the specific language governing permissions and
# limitations under the License.

""" Execute a Process and return the output. """

import subprocess

class ProcessException(Exception):
    """
    Exception that can be raised when an external process execution failed.
    """
    
    def __init__(self, command, exit_code, output):
        """
        Constructor.
        
        :param command: The command that was executed.
        :type command: string
        
        :param exit_code: The exit_code that the external process returned.
        :type exit_code: int
        
        :param ouput: The output of the process.
        :type output: string
        """
        
        self.command = command
        self.output = output
        self.exit_code = exit_code

    def __str__(self):
        """
        Returns the process as string representation.
        
        :return: The stirng representation of this exception.
        :rtype: string
        """
        
        msg = "Command '%s' exited with exit_code %s:\n%s"
        return msg % (self.command, self.exit_code, self.output)

    def __repr__(self):
        return self.__str__()


def execute(command):
    """
    Executes a given command as external process.
    
    :param command: The command that has to be executed.
    :type command: string
    
    :return: Returns the process output.
    :rtype: string
    
    :raises ProcessException: Is raised when the process execution failed.
    """
    
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT)
    output = process.communicate()[0]
    exit_code = process.returncode

    if exit_code == 0:
        return output
    else:
        raise ProcessException(command, exit_code, output)
