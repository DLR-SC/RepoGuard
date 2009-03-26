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
Test methods for the Mantis class.
"""

from configobj import ConfigObj

from repoguard.modules.mantis import Mantis, Config

config_string="""
url=http://localhost/mantis/mc/mantisconnect.php?wsdl
user=administrator
password=root
"""

commit_msg = """
mantis id 3662
Test1
MANTIS ID 3883
Test2
"""

class TestMantis(object):
    
    @classmethod
    def setup_class(cls):
        config = ConfigObj(config_string.splitlines())
        config = Config.from_config(config)
        cls.mantis = Mantis(config)
        
    def test_pattern(self):
        assert self.mantis.extract_issues(commit_msg) == ['3662', '3883']

    def testIssueExists(self):
        assert self.mantis.issue_exists(1)
        assert self.mantis.issue_exists(2)
        assert not self.mantis.issue_exists(1111111111111111)

    def testIssueGetStatus(self):
        self.mantis.issue_get_status("1")

    def testIssueGetHandler(self):
        self.mantis.issue_get_handler("1")
        self.mantis.issue_get_handler("2")

    def testIssueAddNote(self):
        self.mantis.issue_add_note("1", "test")
        
    def testIssueSetCustomFieldIfExists(self):
        self.mantis.issue_set_custom_field("1", "SVNRevision", "123")
