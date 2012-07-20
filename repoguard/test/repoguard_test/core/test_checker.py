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

from repoguard.core import constants
from repoguard.core.checker import RepoGuard


_MAIN_CONFIG = """
template_dirs = resources/templates,
""".splitlines()


_CONFIG_DEFAULT = """
vcs=svn

[profiles]
    [[default]]
        [[[precommit]]]
        default=delayonerror
        checks=PyLint.default, PyLint.default
        error=Console.default,
        success=,
        [[[postcommit]]]
        checks=,
        error=Console.default,
        success=,
    
[checks]
    [[PyLint]]
        [[[default]]]
[handlers]
    [[Console]]
        [[[default]]]
"""


class TestRepoGuard(object):
    
    def setup_method(self, _):
        self._checker = RepoGuard(constants.PRECOMMIT, "/repo/dir")
        self._checker.transaction = mock.Mock()
        self._checker.checks = mock.Mock()
        self._checker.handlers = mock.Mock()
        self._checker.load_config("/template/dir", _CONFIG_DEFAULT.splitlines())

    def test_run_success(self):
        assert self._checker.run() == constants.SUCCESS

    def test_run_error(self):
        self._set_error_entry()
        assert self._checker.run() == constants.ERROR
        assert self._checker.checks.fetch.call_count == 2

    def _set_error_entry(self):
        self._checker.checks.fetch().run.return_value = mock.Mock(result=constants.ERROR)
        self._checker.checks.fetch.reset_mock()
