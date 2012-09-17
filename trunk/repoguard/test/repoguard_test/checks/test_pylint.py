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
Tests the Pylint check.
"""


from configobj import ConfigObj
import mock

from repoguard.checks import pylint_


class TestPyLint(object):

    def setup_method(self, _):
        self._transaction = mock.Mock()
        self._transaction.get_files.return_value = {"filepath":"A"}
        self._transaction.get_file.return_value = "filepath"
        
        self._without_pylintrc = ConfigObj()
        self._with_pylintrc = ConfigObj(["config_file=pylintrc"])
        self._pylint = pylint_.PyLint(self._transaction)
        
    def test_no_files(self):
        self._transaction.get_files.return_value = list()
        assert self._pylint.run(self._without_pylintrc).success
        assert self._pylint.run(self._with_pylintrc).success

    def test_no_modified_files(self):
        self._transaction.get_files.return_value = {"filepath":"D"}
        assert self._pylint.run(self._without_pylintrc).success
        assert self._pylint.run(self._with_pylintrc).success

    def test_success(self):
        pylint_.lint.Run = mock.Mock()
        assert self._pylint.run(self._without_pylintrc).success
        assert self._pylint.run(self._with_pylintrc).success

    def test_failure(self):
        # Let pylint return an error
        pylint_.lint.Run = mock.Mock(side_effect=Exception)
        assert not self._pylint.run(self._without_pylintrc).success
        assert not self._pylint.run(self._with_pylintrc).success
