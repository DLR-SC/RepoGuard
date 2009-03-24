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
Test methods for the AccessRights class.
"""

from configobj import ConfigObj

from repoguard.testutil import TestRepository
from repoguard.checks.accessrights import AccessRights

allow_config_string = """
check_files = test\.java,
allow_users = %s,
"""

deny_config_string = """
check_files = test\.java,
deny_users = %s,
"""

class TestAccessRights:
    
    @classmethod
    def setup_class(cls):
        cls.repository = TestRepository()
        cls.transaction = cls.repository.create_default()[1]

    def test_allow(self):
        global allow_config_string
        allow_config_string = allow_config_string % self.transaction.user_id
        config = ConfigObj(allow_config_string.splitlines())
        accessrights = AccessRights(self.transaction)
        assert accessrights.run(config).success == True
        
    def test_deny(self):
        global deny_config_string
        deny_config_string = deny_config_string % self.transaction.user_id
        config = ConfigObj(deny_config_string.splitlines())
        accessrights = AccessRights(self.transaction)
        assert accessrights.run(config).success == False

