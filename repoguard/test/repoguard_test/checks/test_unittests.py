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
Tests the UnitTests check.
"""


from __future__ import with_statement

from configobj import ConfigObj
import mock

from repoguard.checks import unittests


class TestUnitTests(object):
    
    @classmethod
    def setup_class(cls):
        cls._file_mock = mock.MagicMock(spec=file)
        cls._transaction = mock.Mock()
        
        cls._config = ConfigObj()
        cls._unittests = unittests.UnitTests(cls._transaction)

    def test_skip_interface(self):
        self._transaction.get_files = mock.Mock(return_value={"ApplicationInterface.java":"A"})
        with mock.patch("repoguard.checks.unittests.open", create=True) as open_mock:
            self._init_file_mock(open_mock, "public interface TestInterface {\n}\n")
            assert self._unittests.run(self._config).success
            
    def test_unittest_found(self):
        self._transaction.get_files = mock.Mock(return_value={"ApplicationClass.java":"A"})
        with mock.patch("repoguard.checks.unittests.open", create=True) as open_mock:
            self._init_file_mock(open_mock, "public class TestKlasse {\n}\n")
            self._transaction.file_exists = mock.Mock(return_value=True)
            assert self._unittests.run(self._config).success

    def test_unittest_not_found(self):
        self._transaction.get_files = mock.Mock(return_value={"ApplicationClass.java":"A"})
        with mock.patch("repoguard.checks.unittests.open", create=True) as open_mock:
            self._init_file_mock(open_mock, "public class TestKlasse {\n}\n")
            self._transaction.file_exists = mock.Mock(return_value=False)
            assert not self._unittests.run(self._config).success

    def _init_file_mock(self, open_mock, file_content):
        open_mock.return_value.__enter__.return_value = self._file_mock
        self._file_mock.__iter__ = lambda _: iter(file_content.splitlines())
    
    def test_skip_unittests(self):
        self._transaction.get_files = mock.Mock(return_value={"/test/ApplicationTest.java":"A"})
        assert self._unittests.run(self._config).success
