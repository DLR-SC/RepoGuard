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
This check tests if a unit test exists for a given Java class.
The java class must follow the pattern /main/.../Class.java and
the unit test  must follow the pattern /main/.../TestClass.java. 
Interfaces are omitted.
"""


import re

from repoguard.core.module import Check, ConfigSerializer, Array, String

class Config(ConfigSerializer):
    class types(ConfigSerializer.types):
        check_files = Array(String, optional=True, default=[".*\.java"])
        ignore_files = Array(String, optional=True, default=[])

class UnitTests(Check):

    __config__ = Config

    def _run(self, config):
        files = self.transaction.get_files(config.check_files, 
                                           config.ignore_files)
        interface_pattern = re.compile("interface .* {")
        class_pattern = re.compile("class .* {")
    
        msg = ""
        for filename, attribute in files.iteritems():
            if attribute in ["A", "U", "UU"] and not "/test/" in filename:
    
                # skip java interfaces
                skip = False
                file_object = open(self.transaction.get_file(filename), "r")
                try:
                    for line in file_object:
                        if interface_pattern.search(line):
                            skip = True
                            break
                        elif class_pattern.search(line):
                            break
                finally:
                    file_object.close()
                    
                if skip:
                    continue
    
                unittest = filename.replace("/main/", "/test/")
                unittest = unittest.replace(".java", "Test.java")
                if not self.transaction.file_exists(unittest):
                    msg += "No unittest exists for file %r.\n" % filename
        if msg:
            return self.error(msg)
        else:
            return self.success()
