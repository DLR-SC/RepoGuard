# pylint: disable-msg=W0402,W0232
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
Checks if given files contains non ascii characters.
"""


import string

from repoguard.core.module import Check, ConfigSerializer, Array, String


class Config(ConfigSerializer):
    """
    Configuration of the ASCIIEncoded check.
    """
    
    class types(ConfigSerializer.types):
        check_files = Array(String, optional=True, default=[".*"])
        ignore_files = Array(String, optional=True, default=[])
        include = String(optional=True, default="")
        exclude = String(optional=True, default="")

class ASCIIEncoded(Check):
    """
    Checks if the given files are printable.
    """
    
    __config__ = Config
    
    @staticmethod
    def ascii_check(path, include, exclude):
        """
        Checks if the given file contains non ascii characters.
        
        :param path: The path the file that has to been checked.
        :type path: string
        
        :return: A list of non ascii characters.
        :rtype: list with (row, column, letter) tuples.
        """
        
        result = list()
        row = 1
        include = string.printable + include
        file_object = open(path, 'r')
        try:
            for line in file_object.readlines():
                col = 1
                for letter in line:
                    if not letter in include or letter in exclude:
                        result.append((row, col, line))
                    col += 1
                row += 1
        finally:
            file_object.close()
        return result
    
    @staticmethod
    def format_msg(filename, errors):
        """
        Format the given errors to a more readable format.
        """
        
        msg = []
        msg.append("Unexpected letters in file %s:" % filename)
        for row, col, line in errors:  
            msg.append("%s: %s" % (row, line))
            msg.append("%s %s^" % (" " * len(str(row)), " " * col))
        msg.append("")
        return "\n".join(msg)

    def _run(self, config):
        """
        Executes the check and runs the check.
        
        :param config: The deserialized configuration from the config file.
        :type config: Config
        
        :return: The result of the check.
        :rtype: success(), error()
        """
        
        files = self.transaction.get_files(
            config.check_files, config.ignore_files
        )
        
        msg = ""
        for filename, attribute in files.iteritems():
            if attribute in ["A", "U", "_U", "UU"]:
                filepath = self.transaction.get_file(filename)
                result = self.ascii_check(
                    filepath, config.include, config.exclude
                )
                if result:
                    msg += self.format_msg(filename, result)
        if not msg:
            return self.success()
        else:
            return self.error(msg)
