# pylint: disable-msg=W0232
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
Checks Java files for coding style errors using Checkstyle. 
"""


import os

from repoguard.core import process
from repoguard.core.module import Check, ConfigSerializer, String, Array


class Config(ConfigSerializer):
    """
    Configuration for the Checkstyle check.
    """
    
    paths = []
    
    class types(ConfigSerializer.types):
        check_files = Array(String, optional=True, default=[".*\.java"])
        ignore_files = Array(String, optional=True, default=[])
        java = String
        paths = Array(String)
        config_file = String
        
    def _get_classpath(self):
        """
        Creates the classpath from a defined list of jar files or directories.
        
        :return: Returns all jar files concatinated with a ':'.
        :rtype: string
        """
        
        classpath = []
        for path in self.paths:
            if os.path.isdir(path):
                for jar in os.listdir(path):
                    if jar.endswith('.jar'):
                        path = os.path.join(path, jar)
                        classpath.append(os.path.normpath(path))
            else:
                classpath.append(os.path.normpath(path))
        return ":".join(classpath)
    
    classpath = property(_get_classpath)


class Checkstyle(Check):
    """ Performs Java source code checks using the checkstyle. """ 
    
    __config__ = Config
    
    pattern = "%s -classpath %s com.puppycrawl.tools.checkstyle.Main -c %s %s"

    def _run(self, config):
        """
        Method is called when the check has to run.
        
        :param config: The configuration that has to be used by the check.
        :type config: Config
        
        :return: Returns an error or success messages by calling the success
                 or error method.
        :rtype: Tuple that contains the success or error code and message.
        """
        
        files = self.transaction.get_files(
            config.check_files, config.ignore_files
        )
        
        files = " ".join([
            self.transaction.get_file(filename) 
            for filename, attribute in files.iteritems() 
                 if attribute in ["A", "U", "UU"]
        ])
        
        if files:
            command = self.pattern % (
                config.java, config.classpath, config.config_file, files
            )
            
            self.logger.debug("Running command: %s", command)
            try:
                process.execute(command)
            except process.ProcessException, exc:
                msg = "Coding style errors found:\n\n"
                msg += exc.output + "\n"
                msg += """
                    See Checkstyle documentation for a detailed description: 
                    http://checkstyle.sourceforge.net/
                """
                return self.error(msg)
        
        return self.success()
