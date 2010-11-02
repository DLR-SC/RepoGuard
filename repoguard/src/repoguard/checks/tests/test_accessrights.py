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

ALLOW = True
DENY = False

CONFIGS = (
    ("""
    check_files = test\.java,
    """, DENY),
    ("""
    check_files = test\.java,
    allow_users = test,
    """,  DENY),
    ("""
    check_files = test\.java,
    allow_users = %(user)s,
    """,  ALLOW),
    ("""
    check_files = test\.java,
    deny_users = test,
    """, ALLOW),
    ("""
    check_files = test\.java,
    deny_users = %(user)s,
    """, DENY),
    ("""
    check_files = test\.java,
    allow_users = test_user,
    deny_users = %(user)s,
    """, DENY),
    ("""
    check_files = test\.java,
    allow_users = %(user)s,
    deny_users = test_user,
    """, ALLOW),
    ("""check_files = test\.java,
    allow_users = %(user)s,
    deny_users = %(user)s,
    """, DENY),
    ("""ignore_files = .*,
    allow_users = %(user)s,
    deny_users = %(user)s,
    """, ALLOW),
    ("""ignore_files = .*,
    allow_users = %(user)s,
    """, ALLOW),
    ("""ignore_files = .*,
    deny_users = %(user)s,
    """, ALLOW),
    
    ("""ignore_files = .*,
    """, ALLOW),
)

class TestAccessRights:
    """
    AccessRights Testcase
    """
    
    @classmethod
    def setup_class(cls):
        """
        Setup the test case.
        """
        
        cls.repository = TestRepository()
        cls.transaction = cls.repository.create_default()[1]

    def test_run(self):
        """
        Test for the access rights run method.
        """
        
        for config_string, result in CONFIGS:
            config_string = config_string % {"user" : self.transaction.user_id}
            config = ConfigObj(config_string.splitlines())
            accessrights = AccessRights(self.transaction)
            print config_string, "Allow" if result else "Deny"
            assert accessrights.run(config).success == result
