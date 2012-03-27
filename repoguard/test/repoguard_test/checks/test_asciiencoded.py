# -*- coding: utf-8 -*-
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
Tests the ASCII check.
"""


from configobj import ConfigObj
import mock

from repoguard.checks import asciiencoded


class TestASCIIEncoded(object):
        
    @classmethod
    def setup_class(cls):
        cls._file_mock = mock.MagicMock(spec=file)
        transaction = mock.Mock()
        transaction.get_files = mock.Mock(return_value={"filepath":"A"})
        
        cls._config = ConfigObj(encoding='UTF-8')
        cls._asciiencoded = asciiencoded.ASCIIEncoded(transaction)

    def test_default_contains_ascii_only(self):
        with mock.patch("repoguard.checks.asciiencoded.open", create=True) as open_mock:
            self._init_file_mock(open_mock, '""" doc"""\nprint "hllo@#"')
            assert self._asciiencoded.ascii_check("test.py", "", "") == list()
            
    def test_default_contains_non_ascii(self):
        with mock.patch("repoguard.checks.asciiencoded.open", create=True) as open_mock:
            self._init_file_mock(open_mock, '""" doc"""\nprint "hällo@#"')
            errors = self._asciiencoded.ascii_check("test.py", "", "")
            assert errors[0][1] == 20
            
    def test_include_character(self):
        with mock.patch("repoguard.checks.asciiencoded.open", create=True) as open_mock:
            self._init_file_mock(open_mock, '""" doc"""\nprint "hällo@#"')
            assert self._asciiencoded.ascii_check("test.py", "ä", "") == list()
    
    def test_exclude_character(self):
        with mock.patch("repoguard.checks.asciiencoded.open", create=True) as open_mock:
            self._init_file_mock(open_mock, '""" doc. """\nprint "hell@#"')
            errors = self._asciiencoded.ascii_check("test.py", "", "e")
            assert errors[0][1] == 22
            
    def _init_file_mock(self, open_mock, file_content):
        open_mock.return_value.__enter__.return_value = self._file_mock
        self._file_mock.readlines = mock.Mock(return_value=[file_content])
        
    def test_run_success(self):
        self._asciiencoded.ascii_check = mock.Mock(return_value=list()) 
        assert self._asciiencoded.run(self._config, debug=True).success
        
    def test_run_error(self):
        self._asciiencoded.ascii_check = mock.Mock(return_value=[(0, 0, 0)]) 
        assert not self._asciiencoded.run(self._config, debug=True).success
