# Copyright 2008 Adam Byrtek
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
Reject files with given extensions that include leading tabs. 
"""

from __future__ import with_statement

import re

from repoguard.core.module import Check, ConfigSerializer, String, Array

class Config(ConfigSerializer):
    class types(ConfigSerializer.types):
        check_files = Array(String, optional=True, default=[".*"])
        ignore_files = Array(String, optional=True, default=[])

class RejectTabs(Check):
    """
    
    """
    
    __config__ = Config
    
    pattern = re.compile("^\s*\t")

    def _run(self, config):
        """
        
        """
        
        files = self.transaction.get_files(config.check_files, 
                                           config.ignore_files)
        errors = []
        for filename, attr in files.iteritems():
            if attr not in ["A", "U"]:
                # Process only files which were added or updated
                continue
            if self.transaction.has_property("svn:mime-type", filename):
                mimetype = self.transaction.get_property("svn:mime-type", 
                                                         filename)
                if mimetype == "application/octet-stream":
                    # Skip binary files
                    continue
    
            with open(self.transaction.get_file(filename), "r") as fp:
                msg = "File %s contains leading tabs"
                for line in fp:
                    if self.pattern.match(line):
                        errors.append(msg % filename)
                        break
                    
        return self.success() if not errors else self.error("\n".join(errors))
