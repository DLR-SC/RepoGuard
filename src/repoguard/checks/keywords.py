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
Checks for svn:keywords on all added files in this commit.
 
subversion knows the following keywords for substitution:
svn:keywords  also known as
=======================================
Date          LastChangeDate
Revision      LastChangedRevision | Rev
Author        LastChangedBy
HeadURL       URL
Id
"""


from repoguard.core.module import Check, ConfigSerializer, Array, String
from repoguard.core.transaction import PropertyNotFoundException


class Config(ConfigSerializer):
    class types(ConfigSerializer.types):
        check_files = Array(String, optional=True, default=[".*"])
        ignore_files = Array(String, optional=True, default=[])
        keywords = Array(String)

class Keywords(Check):
    """
    Check for svn:keywords on all added files in this commit.
    """
    
    __config__ = Config

    pattern = "Property 'svn:keywords' on file '%s' is missing keyword '%s'.\n"

    def _run(self, config):
        """
        Executes the keywords check for all added or updates files.
        
        :param config: The configuration that has to be used.
        :type config: Config object.
        """
        
        files = self.transaction.get_files(
            config.check_files, config.ignore_files
        )
        
        msg = ""    
        for filename, attribute in files.iteritems():
            if attribute in ["A", "U", "_U", "UU"]:
                try:
                    keywords_is = self.transaction.get_property(
                        "svn:keywords", filename
                    )
                except PropertyNotFoundException:
                    keywords_is = ""
                
                for keyword in config.keywords:
                    if keyword not in keywords_is:
                        msg += self.pattern % (filename, keyword) 
        if msg:
            return self.error(msg)
        else:
            return self.success()
