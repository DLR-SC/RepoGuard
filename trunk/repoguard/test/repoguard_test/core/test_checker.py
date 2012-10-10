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


""" Tests the RepoGuard main class. """


import mock
import random

from repoguard.core import constants, transaction
from repoguard.core.checker import RepoGuard


_CONFIG_DEFAULT = """
vcs=svn

[profiles]
    [[default]]
        [[[precommit]]]
        default=delayonerror
        checks=Mantis.default,
        error=Console.default,
        success=,
        [[[postcommit]]]
        checks=,
        error=Console.default,
        success=,
        
    [[ProjectA]]
        regex=^ProjectA
        [[[precommit]]]
        default=delayonerror
        checks=PyLint.default,
        error=,
        success=,
        
    [[ProjectB]]
        regex=^ProjectB
        [[[precommit]]]
        default=delayonerror
        checks=Checkstyle.default,
        error=,
        success=,
    
[checks]
    [[PyLint]]
        [[[default]]]
    [[Checkstyle]]
        [[[default]]]
    [[Mantis]]
        [[[default]]]
[handlers]
    [[Console]]
        [[[default]]]
"""


class TestRepoGuard(object):
    
    def setup_method(self, _):
        self._checker = RepoGuard(constants.PRECOMMIT, "/repo/dir")
        self._checker.checks = mock.Mock()
        self._checker.handlers = mock.Mock()
        
        self._checker.transaction = transaction.Transaction("/path/to/repository", "10")
        self._checker.transaction._execute_svn = mock.Mock(return_value=dict())
        
        self._checker.load_config("/template/dir", _CONFIG_DEFAULT.splitlines())

    def test_run_success(self):
        assert self._checker.run() == constants.SUCCESS

    def test_run_error(self):
        self._set_error_entry()
        self._set_transaction_changeset(["A   Project/vendors/deli/"])
        assert self._checker.run() == constants.ERROR
        
    def _set_error_entry(self):
        self._checker.checks.fetch().run.return_value = mock.Mock(result=constants.ERROR)
        self._checker.checks.fetch.reset_mock()

    def _set_transaction_changeset(self, changeset):
        # pylint: disable=W0212
        # Access to non-public method is fine for testing.
        self._checker.transaction._execute_svn.return_value = changeset

    def test_match_default_profile(self):
        self._set_transaction_changeset(["A   Project/vendors/deli/"])
        self._checker.run()
        assert self._checker.checks.fetch.call_count == 1
        assert self._checker.checks.fetch.call_args[0][0] == "Mantis"
        
    def test_match_projecta_profile(self):
        self._set_transaction_changeset(["A   ProjectA/vendors/deli/"])
        self._checker.run()
        assert self._checker.checks.fetch.call_count == 1
        assert self._checker.checks.fetch.call_args[0][0] == "PyLint"
        
    def test_match_projectb_profile(self):
        self._set_transaction_changeset(["A   ProjectB/vendors/deli/"])
        self._checker.run()
        assert self._checker.checks.fetch.call_count == 1
        assert self._checker.checks.fetch.call_args[0][0] == "Checkstyle"
        
    def test_match_all_profiles(self):
        self._set_transaction_changeset([
            "A   ProjectB/vendors/deli/", "A   ProjectA/vendors/deli/", "A   Project/vendors/deli/"])
        self._checker.run()
        assert self._checker.checks.fetch.call_count == 3
        assert self._checker.checks.fetch.call_args_list[0][0][0] == "Mantis"
        assert self._checker.checks.fetch.call_args_list[1][0][0] == "PyLint"
        assert self._checker.checks.fetch.call_args_list[2][0][0] == "Checkstyle"
        
    def test_large_default_profile_changeset(self):
        large_changset = list()
        for _ in range(10000):
            large_changset.append("A   Project/vendors/deli%f" % random.random())
        self._set_transaction_changeset(large_changset)
        self._checker.run()

    def test_run_profile_success(self):
        self._checker.run_profile("ProjectA")
        
        assert self._checker.checks.fetch.call_count == 1
        assert self._checker.checks.fetch.call_args[0][0] == "PyLint"
        
    def test_run_missing_profile(self):
        self._checker.run_profile("UNDEFINED_PROFILE")
        
        assert self._checker.checks.fetch.call_count == 0
