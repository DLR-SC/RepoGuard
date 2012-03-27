#
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
Tests the RejectTabs check.
"""


from configobj import ConfigObj
import mock

from repoguard.checks import rejecttabs


class TestRejectTabs(object):

    def setup_method(self, _):
        self._file_mock = mock.MagicMock()
        self._transaction = mock.Mock()
        self._transaction.get_files = mock.Mock(return_value={"filepath":"A"})
        
        self._config = ConfigObj()
        self._rejecttabs = rejecttabs.RejectTabs(self._transaction)

    def test_leading_tab(self):
        with mock.patch("repoguard.checks.rejecttabs.open", create=True) as open_mock:
            self._init_file_mock(open_mock, 'if True:\n\tprint "Hello world"')
            assert not self._rejecttabs.run(self._config).success
        
    def test_leading_mixed_tab_space(self):
        with mock.patch("repoguard.checks.rejecttabs.open", create=True) as open_mock:
            self._init_file_mock(open_mock, 'if True:\n \tprint "Hello world"')
            assert not self._rejecttabs.run(self._config).success
    
    def test_inner_tab(self):
        with mock.patch("repoguard.checks.rejecttabs.open", create=True) as open_mock:
            self._init_file_mock(open_mock, 'if True:\n    print "\tHello world"')
            assert self._rejecttabs.run(self._config).success
        
    def _init_file_mock(self, open_mock, file_content):
        open_mock.return_value.__enter__.return_value = self._file_mock
        self._file_mock.__iter__ = lambda _: iter(file_content.splitlines())
    
    def test_skip_binary_files(self):
        self._transaction.has_property = mock.Mock(return_value=True)
        self._transaction.get_property = mock.Mock(return_value="application/octet-stream")
        assert self._rejecttabs.run(self._config).success
