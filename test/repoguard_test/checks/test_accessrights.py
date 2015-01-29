#
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
Tests the AccessRights check.
"""


import configobj
import mock

from repoguard.checks import accessrights


class TestAccessRights(object):
    
    def setup_method(self, _):
        self._transaction = mock.Mock(user_id="me")
        self._transaction.get_files = mock.Mock(return_value={"test.java":"A"})
        
        self._accessrights = accessrights.AccessRights(self._transaction)
        
    def test_default_configuration(self):
        config = self._get_config(list())
        assert not self._accessrights.run(config).success

    def test_ignore(self):
        self._transaction.get_files.return_value = dict()
        config = self._get_config(["ignore_files = .*,"])
        assert self._accessrights.run(config).success
        config = self._get_config(
            ["ignore_files = .*,", "allow_users = me,"])
        assert self._accessrights.run(config).success
        config = self._get_config(
            ["ignore_files = .*,", "deny_users = me,"])
        assert self._accessrights.run(config).success
        config = self._get_config(
            ["ignore_files = .*,", "allow_users = me,", "deny_users = me,"])
        assert self._accessrights.run(config).success
    
    def test_check_without_user(self):
        config = self._get_config(["check_files = test\.java,"])
        assert not self._accessrights.run(config).success
    
    def test_check_with_allowed_users_only(self):
        config = self._get_config(
            ["check_files = test\.java,", "allow_users = anotheruser,"])
        assert not self._accessrights.run(config).success
        config = self._get_config(
            ["check_files = test\.java,", "allow_users = me,"])
        assert self._accessrights.run(config).success
        
    def test_check_with_denied_users_only(self):
        config = self._get_config(
            ["check_files = test\.java,", "deny_users = anotheruser,"])
        assert self._accessrights.run(config).success
        config = self._get_config(
            ["check_files = test\.java,", "deny_users = me,"])
        assert not self._accessrights.run(config).success
        
    def test_check_with_allowed_and_denied_users(self):
        config = self._get_config(
            ["check_files = test\.java,", "allow_users = anotheruser,", "deny_users = me,"])
        assert not self._accessrights.run(config).success
        config = self._get_config(
            ["check_files = test\.java,", "allow_users = me,", "deny_users = anotheruser,"])
        assert self._accessrights.run(config).success
        config = self._get_config(
            ["check_files = test\.java,", "allow_users = me,", "deny_users = me,"])
        assert not self._accessrights.run(config).success
        
    @staticmethod
    def _get_config(parameters):
        return configobj.ConfigObj(parameters)
